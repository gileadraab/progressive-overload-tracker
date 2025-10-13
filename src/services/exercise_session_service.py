from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from src.models.exercise_session import ExerciseSession
from src.schemas.exercise_session import (ExerciseSessionCreate,
                                          ExerciseSessionUpdate)


def get_exercise_sessions(
    db: DbSession, skip: int = 0, limit: int = 100
) -> List[ExerciseSession]:
    """
    Get all exercise sessions from the database.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of all exercise sessions.
    """
    result = db.execute(
        select(ExerciseSession)
        .options(
            joinedload(ExerciseSession.exercise),
            joinedload(ExerciseSession.session),
            joinedload(ExerciseSession.template),
            joinedload(ExerciseSession.sets),
        )
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().unique().all())


def get_exercise_session(exercise_session_id: int, db: DbSession) -> ExerciseSession:
    """
    Get a single exercise session by its ID.

    Args:
        exercise_session_id: The ID of the exercise session to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the exercise session with the given ID is not found.

    Returns:
        The retrieved exercise session.
    """
    result = db.execute(
        select(ExerciseSession)
        .options(
            joinedload(ExerciseSession.exercise),
            joinedload(ExerciseSession.session),
            joinedload(ExerciseSession.template),
            joinedload(ExerciseSession.sets),
        )
        .where(ExerciseSession.id == exercise_session_id)
    )
    exercise_session = result.scalars().first()

    if not exercise_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ExerciseSession with id {exercise_session_id} not found",
        )
    return exercise_session


def create_exercise_session(
    exercise_session_data: ExerciseSessionCreate, db: DbSession
) -> ExerciseSession:
    """
    Create a new exercise session in the database.

    Args:
        exercise_session_data: The exercise session data to create.
        db: The database session.

    Returns:
        The newly created exercise session.
    """
    db_exercise_session = ExerciseSession(**exercise_session_data.model_dump())
    db.add(db_exercise_session)
    db.commit()
    db.refresh(db_exercise_session)
    return get_exercise_session(int(db_exercise_session.id), db)


def update_exercise_session(
    exercise_session_id: int,
    exercise_session_data: ExerciseSessionUpdate,
    db: DbSession,
) -> ExerciseSession:
    """
    Update an existing exercise session in the database.

    Args:
        exercise_session_id: The ID of the exercise session to update.
        exercise_session_data: The exercise session data to update.
        db: The database session.

    Raises:
        HTTPException: If the exercise session with the given ID is not found.

    Returns:
        The updated exercise session.
    """
    db_exercise_session = db.get(ExerciseSession, exercise_session_id)
    if not db_exercise_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ExerciseSession with id {exercise_session_id} not found",
        )

    update_data = exercise_session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exercise_session, field, value)

    db.commit()
    db.refresh(db_exercise_session)
    return get_exercise_session(exercise_session_id, db)


def delete_exercise_session(exercise_session_id: int, db: DbSession) -> None:
    """
    Delete an exercise session from the database.

    Args:
        exercise_session_id: The ID of the exercise session to delete.
        db: The database session.

    Raises:
        HTTPException: If the exercise session with the given ID is not found.
    """
    exercise_session = db.get(ExerciseSession, exercise_session_id)
    if not exercise_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ExerciseSession with id {exercise_session_id} not found",
        )
    db.delete(exercise_session)
    db.commit()
