from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from src.models.enums import UnitEnum


class SetBase(BaseModel):
    """Base Set schema with common fields."""
    weight: float = Field(..., gt=0, description="Weight used for the set")
    reps: int = Field(..., gt=0, description="Number of repetitions")
    unit: UnitEnum = Field(..., description="Unit of measurement (kg or stacks)")
    exercise_session_id: int = Field(..., description="ID of the exercise session this set belongs to")


class SetCreate(SetBase):
    """Schema for creating a new set."""
    pass


class SetUpdate(BaseModel):
    """Schema for updating an existing set."""
    weight: Optional[float] = Field(None, gt=0)
    reps: Optional[int] = Field(None, gt=0)
    unit: Optional[UnitEnum] = Field(None)
    exercise_session_id: Optional[int] = Field(None)


class SetResponse(SetBase):
    """Schema for set responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class SetWithExerciseSession(SetResponse):
    """Schema for set with exercise session details included."""
    from src.schemas.exercise_session import ExerciseSessionResponse

    exercise_session: ExerciseSessionResponse

    model_config = ConfigDict(from_attributes=True)