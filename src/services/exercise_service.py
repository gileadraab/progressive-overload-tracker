from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.exercise import Exercise
from src.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse


def get_exercises(db: Session, skip: int = 0, limit: int = 100) -> List[Exercise]:
    """
    Get all exercises from the database.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of exercises.
    """
    result = db.execute(select(Exercise).offset(skip).limit(limit))
    return result.scalars().all()


def search_exercises(query: str, db: Session) -> List[Exercise]:
    """
    Search exercises by name, category, or subcategory.

    Args:
        query: The search term.
        db: The database session.

    Returns:
        A list of exercises matching the search query.
    """
    search = f"%{query}%"
    result = db.execute(
        select(Exercise).where(
            (Exercise.name.ilike(search))
            | (Exercise.category.cast(db.bind.dialect.name).ilike(search))
            | (Exercise.subcategory.ilike(search))
        )
    )
    return result.scalars().all()


def get_exercise(exercise_id: int, db: Session) -> Exercise:
    """
    Get a single exercise by its ID.

    Args:
        exercise_id: The ID of the exercise to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.

    Returns:
        The retrieved exercise.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    return exercise


def create_exercise(exercise: ExerciseCreate, db: Session) -> Exercise:
    """
    Create a new exercise in the database.

    Args:
        exercise: The exercise data to create.
        db: The database session.

    Returns:
        The newly created exercise.
    """
    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def update_exercise(
    exercise_id: int, exercise: ExerciseUpdate, db: Session
) -> Exercise:
    """
    Update an existing exercise in the database.

    Args:
        exercise_id: The ID of the exercise to update.
        exercise: The exercise data to update.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.

    Returns:
        The updated exercise.
    """
    db_exercise = db.get(Exercise, exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    update_data = exercise.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exercise, field, value)

    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(exercise_id: int, db: Session) -> None:
    """
    Delete an exercise from the database.

    Args:
        exercise_id: The ID of the exercise to delete.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    db.delete(exercise)
    db.commit()
