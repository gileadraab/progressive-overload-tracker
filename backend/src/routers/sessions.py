from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemas.session import SessionCreate, SessionUpdate, SessionWithDetails
from src.services import session_service, template_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=List[SessionWithDetails])
def list_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a list of workout sessions for the authenticated user.

    Requires authentication. Returns only sessions belonging to the current user.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    # Only return sessions for the authenticated user
    user_id: int = int(current_user.id) if current_user.id else 0
    return session_service.get_sessions(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{session_id}", response_model=SessionWithDetails)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific workout session by ID, including exercises and sets.

    Requires authentication. Users can only view their own sessions.

    - **session_id**: The ID of the session to retrieve
    """
    session = session_service.get_session(session_id, db)
    # Verify session belongs to current user
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )
    return session


@router.post(
    "/", response_model=SessionWithDetails, status_code=status.HTTP_201_CREATED
)
def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new workout session with nested exercises and sets.

    Requires authentication. The session will be created for the authenticated user.

    - **user_id**: Must match the authenticated user's ID
    - **date**: Optional session date and time (defaults to now)
    - **exercise_sessions**: List of exercises in this session, each with:
      - **exercise_id**: ID of the exercise
      - **sets**: List of sets for this exercise, each with:
        - **weight**: Weight used
        - **reps**: Number of repetitions
        - **unit**: Unit of measurement (kg or stacks)
    """
    # Verify session is being created for the authenticated user
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create session for another user",
        )
    return session_service.create_session(session, db)


@router.put("/{session_id}", response_model=SessionWithDetails)
def update_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing workout session with full editing support.

    Requires authentication. Users can only update their own sessions.

    This endpoint supports two modes:
    1. **Partial update**: Update only date/notes (omit exercise_sessions)
    2. **Full replacement**: Replace all exercises and sets (include exercise_sessions)

    **Workflow for full editing:**
    - GET /sessions/{id} to fetch current session
    - Modify the data in your application
    - PUT /sessions/{id} with the modified data
    - All existing exercise_sessions and sets are replaced atomically

    **Use cases:**
    - Fix weight typos (e.g., 1000kg -> 100kg)
    - Add forgotten exercises
    - Remove incorrect sets
    - Correct historical data

    - **session_id**: The ID of the session to update
    - **date**: Optional updated date/time
    - **notes**: Optional updated notes
    - **exercise_sessions**: Optional complete replacement of exercises/sets
    """
    # Verify session belongs to current user
    existing_session = session_service.get_session(session_id, db)
    if existing_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this session",
        )
    return session_service.update_session(session_id, session, db)


@router.get("/from-template/{template_id}", response_model=SessionCreate)
def get_session_from_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a session structure from a template to use as starting point for a new session.

    Requires authentication. Creates session structure for the authenticated user.

    This endpoint returns data in SessionCreate format that can be:
    1. Modified by the frontend (add sets, change exercises)
    2. Submitted to POST /sessions/ to create a new workout

    **Workflow:**
    - User selects a saved template
    - Frontend receives exercise list with empty sets
    - User fills in weights/reps during workout
    - Frontend submits to POST /sessions/ to save

    - **template_id**: The ID of the template to use
    """
    user_id: int = int(current_user.id) if current_user.id else 0
    return template_service.get_template_as_session(template_id, user_id, db)


@router.get("/from-session/{session_id}", response_model=SessionCreate)
def get_session_copy(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Copy a previous session to use as starting point for a new workout.

    Requires authentication. Users can only copy their own sessions.

    This is the PRIMARY progressive overload workflow - "repeat last workout".
    Users copy their previous workout, modify weights/reps for progression,
    and submit to POST /sessions/ to save the improved version.

    This endpoint returns data in SessionCreate format that can be:
    1. Modified by the frontend (increase weights, adjust reps, add sets)
    2. Submitted to POST /sessions/ to create a new workout

    **Workflow:**
    - User clicks "Repeat last workout"
    - Frontend receives previous exercises and sets with weights
    - User modifies (e.g., increase bench press from 100kg to 102.5kg)
    - Frontend submits to POST /sessions/ to save

    **Example:**
    ```
    GET /sessions/from-session/42
    # Returns SessionCreate with previous workout data
    # User increases weights in UI
    POST /sessions/ with modified data
    # Creates new session with progressive overload
    ```

    - **session_id**: The ID of the session to copy
    """
    # Verify session belongs to current user before copying
    existing_session = session_service.get_session(session_id, db)
    if existing_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to copy this session",
        )
    user_id: int = int(current_user.id) if current_user.id else 0
    return session_service.get_session_as_template(session_id, user_id, db)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a workout session.

    Requires authentication. Users can only delete their own sessions.

    - **session_id**: The ID of the session to delete
    - This will cascade delete all associated exercise_sessions and sets
    """
    # Verify session belongs to current user
    existing_session = session_service.get_session(session_id, db)
    if existing_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session",
        )
    session_service.delete_session(session_id, db)
    return None
