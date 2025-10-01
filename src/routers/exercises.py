from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse
from src.services import exercise_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=List[ExerciseResponse])
def list_exercises(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name, category, or subcategory"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of exercises.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **search**: Optional search term to filter exercises
    """
    if search:
        return exercise_service.search_exercises(search, db)
    return exercise_service.get_exercises(db, skip=skip, limit=limit)


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific exercise by ID.

    - **exercise_id**: The ID of the exercise to retrieve
    """
    return exercise_service.get_exercise(exercise_id, db)


@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new exercise.

    - **name**: Name of the exercise
    - **category**: Exercise category (chest, back, legs, shoulders, arms, core)
    - **subcategory**: Optional subcategory (e.g., "Upper Chest")
    - **equipment**: Optional equipment type (machine, dumbbell, barbell, bodyweight, kettlebell, resistance_band)
    - **image_url**: Optional URL to an image of the exercise
    """
    return exercise_service.create_exercise(exercise, db)


@router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise: ExerciseUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing exercise.

    - **exercise_id**: The ID of the exercise to update
    - All fields are optional; only provided fields will be updated
    """
    return exercise_service.update_exercise(exercise_id, exercise, db)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an exercise.

    - **exercise_id**: The ID of the exercise to delete
    """
    exercise_service.delete_exercise(exercise_id, db)
    return None
