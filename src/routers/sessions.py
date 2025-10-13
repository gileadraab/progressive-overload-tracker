from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.session import (SessionCreate, SessionUpdate,
                                 SessionWithDetails)
from src.services import session_service, template_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=List[SessionWithDetails])
def list_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of workout sessions with their exercises and sets.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **user_id**: Optional filter to get sessions for a specific user
    """
    return session_service.get_sessions(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{session_id}", response_model=SessionWithDetails)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific workout session by ID, including exercises and sets.

    - **session_id**: The ID of the session to retrieve
    """
    return session_service.get_session(session_id, db)


@router.post(
    "/", response_model=SessionWithDetails, status_code=status.HTTP_201_CREATED
)
def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new workout session with nested exercises and sets.

    - **user_id**: ID of the user who owns this session
    - **date**: Optional session date and time (defaults to now)
    - **exercise_sessions**: List of exercises in this session, each with:
      - **exercise_id**: ID of the exercise
      - **sets**: List of sets for this exercise, each with:
        - **weight**: Weight used
        - **reps**: Number of repetitions
        - **unit**: Unit of measurement (kg or stacks)
    """
    return session_service.create_session(session, db)


@router.put("/{session_id}", response_model=SessionWithDetails)
def update_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing workout session.

    - **session_id**: The ID of the session to update
    - All fields are optional; only provided fields will be updated
    - Note: This endpoint updates session metadata only, not nested exercises/sets
    """
    return session_service.update_session(session_id, session, db)


@router.get("/from-template/{template_id}", response_model=SessionCreate)
def get_session_from_template(
    template_id: int,
    user_id: int = Query(..., description="User ID for the new session"),
    db: Session = Depends(get_db),
):
    """
    Get a session structure from a template to use as starting point for a new session.

    This endpoint returns data in SessionCreate format that can be:
    1. Modified by the frontend (add sets, change exercises)
    2. Submitted to POST /sessions/ to create a new workout

    **Workflow:**
    - User selects a saved template
    - Frontend receives exercise list with empty sets
    - User fills in weights/reps during workout
    - Frontend submits to POST /sessions/ to save

    - **template_id**: The ID of the template to use
    - **user_id**: The ID of the user for the new session
    """
    return template_service.get_template_as_session(template_id, user_id, db)


@router.get("/from-session/{session_id}", response_model=SessionCreate)
def get_session_copy(
    session_id: int,
    user_id: int = Query(..., description="User ID for the new session"),
    db: Session = Depends(get_db),
):
    """
    Copy a previous session to use as starting point for a new workout.

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
    GET /sessions/from-session/42?user_id=1
    # Returns SessionCreate with previous workout data
    # User increases weights in UI
    POST /sessions/ with modified data
    # Creates new session with progressive overload
    ```

    - **session_id**: The ID of the session to copy
    - **user_id**: The ID of the user for the new session
    """
    return session_service.get_session_as_template(session_id, user_id, db)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a workout session.

    - **session_id**: The ID of the session to delete
    - This will cascade delete all associated exercise_sessions and sets
    """
    session_service.delete_session(session_id, db)
    return None
