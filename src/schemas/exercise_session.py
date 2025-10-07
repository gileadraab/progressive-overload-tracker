from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from src.schemas.exercise import ExerciseResponse
    from src.schemas.session import SessionResponse
    from src.schemas.template import TemplateResponse
    from src.schemas.set import SetResponse


class ExerciseSessionBase(BaseModel):
    """Base ExerciseSession schema with common fields."""
    exercise_id: int = Field(..., description="ID of the exercise")
    session_id: Optional[int] = Field(None, description="ID of the session (if part of a workout)")
    template_id: Optional[int] = Field(None, description="ID of the template (if part of a template)")


class ExerciseSessionCreate(ExerciseSessionBase):
    """Schema for creating a new exercise session."""
    sets: List["SetCreate"] = Field(default_factory=list, description="Sets for this exercise")


class ExerciseSessionUpdate(BaseModel):
    """Schema for updating an existing exercise session."""
    exercise_id: Optional[int] = Field(None)
    session_id: Optional[int] = Field(None)
    template_id: Optional[int] = Field(None)


class ExerciseSessionResponse(ExerciseSessionBase):
    """Schema for exercise session responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class ExerciseSessionWithDetails(ExerciseSessionResponse):
    """Schema for exercise session with full details included."""
    exercise: Optional["ExerciseResponse"] = None
    session: Optional["SessionResponse"] = None
    template: Optional["TemplateResponse"] = None
    sets: List["SetResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import for forward reference resolution
from src.schemas.set import SetCreate  # noqa: E402