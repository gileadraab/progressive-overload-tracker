from typing import List
from sqlalchemy.orm import Session as DbSession, joinedload
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.session import Session as SessionModel
from src.models.exercise_session import ExerciseSession
from src.models.set import Set as SetModel
from src.models.user import User
from src.models.exercise import Exercise
from src.schemas.session import SessionCreate, SessionUpdate


def get_sessions(db: DbSession, skip: int = 0, limit: int = 100) -> List[SessionModel]:
    """
    Get all workout sessions from the database.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of all sessions.
    """
    result = db.execute(
        select(SessionModel)
        .options(
            joinedload(SessionModel.exercise_sessions).options(
                joinedload(ExerciseSession.exercise),
                joinedload(ExerciseSession.sets)
            ),
            joinedload(SessionModel.user)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().unique().all()


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
                joinedload(ExerciseSession.exercise),
                joinedload(ExerciseSession.sets)
            ),
            joinedload(SessionModel.user)
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
    user = db.get(User, session_dict['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {session_dict['user_id']} not found"
        )

    # Extract nested exercise_sessions if present
    exercise_sessions_data = session_dict.pop('exercise_sessions', [])

    # Validate all exercises exist
    for es_data in exercise_sessions_data:
        exercise = db.get(Exercise, es_data['exercise_id'])
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {es_data['exercise_id']} not found"
            )

    # Create the session
    db_session = SessionModel(**session_dict)

    # Add nested exercise sessions and sets
    for es_data in exercise_sessions_data:
        sets_data = es_data.pop('sets', [])
        db_es = ExerciseSession(**es_data)

        for set_data in sets_data:
            db_set = SetModel(**set_data)
            db_es.sets.append(db_set)

        db_session.exercise_sessions.append(db_es)

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return get_session(db_session.id, db)


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
