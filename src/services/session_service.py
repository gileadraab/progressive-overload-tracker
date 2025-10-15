from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as SessionModel
from src.models.set import Set as SetModel
from src.models.user import User
from src.schemas.exercise_session import ExerciseSessionCreate
from src.schemas.session import SessionCreate, SessionReorderRequest, SessionUpdate
from src.schemas.set import SetCreate


def get_sessions(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
) -> List[SessionModel]:
    """
    Get all workout sessions from the database with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        user_id: Optional user_id filter to get sessions for a specific user.

    Returns:
        A list of all sessions.
    """
    query = select(SessionModel).options(
        joinedload(SessionModel.exercise_sessions).options(
            joinedload(ExerciseSession.exercise), joinedload(ExerciseSession.sets)
        ),
        joinedload(SessionModel.user),
    )

    if user_id:
        query = query.where(SessionModel.user_id == user_id)

    result = db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().unique().all())


def get_session(session_id: int, db: DbSession) -> SessionModel:
    """
    Get a single session by its ID, including its exercises and sets.

    Args:
        session_id: The ID of the session to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.

    Returns:
        The retrieved session.
    """
    result = db.execute(
        select(SessionModel)
        .options(
            joinedload(SessionModel.exercise_sessions).options(
                joinedload(ExerciseSession.exercise), joinedload(ExerciseSession.sets)
            ),
            joinedload(SessionModel.user),
        )
        .where(SessionModel.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )
    return session


def create_session(session_data: SessionCreate, db: DbSession) -> SessionModel:
    """
    Create a new session with nested exercises and sets.

    Args:
        session_data: The session data, including nested exercise sessions and sets.
        db: The database session.

    Raises:
        HTTPException: If user_id or any exercise_id does not exist.

    Returns:
        The newly created session.
    """
    session_dict = session_data.model_dump()

    # Validate user exists
    user = db.get(User, session_dict["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {session_dict['user_id']} not found",
        )

    # Extract nested exercise_sessions if present
    exercise_sessions_data = session_dict.pop("exercise_sessions", [])

    # Validate all exercises exist
    for es_data in exercise_sessions_data:
        exercise = db.get(Exercise, es_data["exercise_id"])
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {es_data['exercise_id']} not found",
            )

    # Create the session
    db_session = SessionModel(**session_dict)

    # Add nested exercise sessions and sets
    for es_index, es_data in enumerate(exercise_sessions_data, start=1):
        sets_data = es_data.pop("sets", [])
        # Assign order based on position if not provided
        if "order" not in es_data or es_data["order"] is None:
            es_data["order"] = es_index
        db_es = ExerciseSession(**es_data)

        for set_index, set_data in enumerate(sets_data, start=1):
            # Assign order based on position if not provided
            if "order" not in set_data or set_data["order"] is None:
                set_data["order"] = set_index
            db_set = SetModel(**set_data)
            db_es.sets.append(db_set)

        db_session.exercise_sessions.append(db_es)

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return get_session(int(db_session.id), db)


def update_session(
    session_id: int, session_data: SessionUpdate, db: DbSession
) -> SessionModel:
    """
    Update an existing session.

    Args:
        session_id: The ID of the session to update.
        session_data: The session data to update.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.

    Returns:
        The updated session.
    """
    db_session = db.get(SessionModel, session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )

    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)

    db.commit()
    db.refresh(db_session)
    return get_session(session_id, db)


def delete_session(session_id: int, db: DbSession) -> None:
    """
    Delete a session from the database.

    Args:
        session_id: The ID of the session to delete.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.
    """
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )
    db.delete(session)
    db.commit()


def get_session_as_template(
    session_id: int, user_id: int, db: DbSession
) -> SessionCreate:
    """
    Get a session structure that can be used to create a new session (copy workflow).

    This enables the "repeat last workout" functionality where users copy a previous
    session as a starting point, modify weights/reps, and save as a new session.

    Args:
        session_id: The ID of the session to copy.
        user_id: The user_id for the new session.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.

    Returns:
        SessionCreate object with exercises and sets from the source session.
    """
    # Fetch the source session with all nested data
    source_session = get_session(session_id, db)

    # Build exercise_sessions list in the format expected by SessionCreate
    exercise_sessions_data = []
    for es in source_session.exercise_sessions:
        # Build sets list for this exercise
        sets_data = [
            SetCreate(
                weight=set_obj.weight,
                reps=set_obj.reps,
                unit=set_obj.unit,
                order=set_obj.order,
                exercise_session_id=None,
            )
            for set_obj in es.sets
        ]

        # Build exercise_session
        exercise_sessions_data.append(
            ExerciseSessionCreate(
                exercise_id=es.exercise_id,
                session_id=None,
                template_id=None,
                order=es.order,
                sets=sets_data,
            )
        )

    # Return SessionCreate with current user_id and copied exercises/sets
    return SessionCreate(
        user_id=user_id,
        date=None,  # Will be set to current time when created
        exercise_sessions=exercise_sessions_data,
    )


def reorder_session(
    session_id: int, reorder_data: SessionReorderRequest, db: DbSession
) -> SessionModel:
    """
    Reorder exercise sessions and/or sets within a session.

    This allows users to rearrange the order of exercises and sets
    via drag-and-drop in the frontend.

    Args:
        session_id: The ID of the session to reorder.
        reorder_data: The reorder request with new order values.
        db: The database session.

    Raises:
        HTTPException: If the session is not found.
        HTTPException: If any exercise_session or set doesn't belong to this session.

    Returns:
        The updated session with reordered exercises/sets.
    """
    # Verify session exists
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )

    # Update exercise_session and set orders
    for es_update in reorder_data.exercise_sessions:
        db_es = db.get(ExerciseSession, es_update.id)
        if not db_es:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ExerciseSession with id {es_update.id} not found",
            )

        # Verify exercise_session belongs to this session
        if db_es.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ExerciseSession {es_update.id} does not belong to session {session_id}",
            )

        # Update exercise_session order if provided
        if es_update.order is not None:
            db_es.order = es_update.order

        # Update set orders if provided
        if es_update.sets:
            for set_update in es_update.sets:
                db_set = db.get(SetModel, set_update.id)
                if not db_set:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Set with id {set_update.id} not found",
                    )

                # Verify set belongs to this exercise_session
                if db_set.exercise_session_id != es_update.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Set {set_update.id} does not belong to exercise_session {es_update.id}",
                    )

                db_set.order = set_update.order

    db.commit()
    return get_session(session_id, db)
