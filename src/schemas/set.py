from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from src.models.enums import UnitEnum

if TYPE_CHECKING:
    from src.schemas.exercise_session import ExerciseSessionResponse


class SetBase(BaseModel):
    """Base Set schema with common fields."""
    weight: float = Field(..., gt=0, description="Weight used for the set")
    reps: int = Field(..., gt=0, description="Number of repetitions")
    unit: UnitEnum = Field(..., description="Unit of measurement (kg or stacks)")


class SetCreate(SetBase):
    """Schema for creating a new set."""
    exercise_session_id: Optional[int] = Field(None, description="ID of the exercise session (optional for nested creation)")


class SetUpdate(BaseModel):
    """Schema for updating an existing set."""
    weight: Optional[float] = Field(None, gt=0)
    reps: Optional[int] = Field(None, gt=0)
    unit: Optional[UnitEnum] = Field(None)
    exercise_session_id: Optional[int] = Field(None)


class SetResponse(SetBase):
    """Schema for set responses."""
    id: int
    exercise_session_id: int

    model_config = ConfigDict(from_attributes=True)


class SetWithExerciseSession(SetResponse):
    """Schema for set with exercise session details included."""
    exercise_session: Optional["ExerciseSessionResponse"] = None

    model_config = ConfigDict(from_attributes=True)