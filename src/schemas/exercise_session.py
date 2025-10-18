from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.exercise import ExerciseResponse
    from src.schemas.session import SessionResponse
    from src.schemas.set import SetResponse
    from src.schemas.template import TemplateResponse


class ExerciseSessionBase(BaseModel):
    """Base ExerciseSession schema with common fields."""

    exercise_id: int = Field(..., description="ID of the exercise")
    session_id: Optional[int] = Field(
        None, description="ID of the session (if part of a workout)"
    )
    template_id: Optional[int] = Field(
        None, description="ID of the template (if part of a template)"
    )
    order: Optional[int] = Field(
        None, description="Display order within session or template"
    )


class ExerciseSessionCreate(BaseModel):
    """Schema for creating a new exercise session."""

    exercise_id: int = Field(..., description="ID of the exercise")
    session_id: Optional[int] = Field(
        None, description="ID of the session (if part of a workout)"
    )
    template_id: Optional[int] = Field(
        None, description="ID of the template (if part of a template)"
    )
    order: Optional[int] = Field(
        None, description="Display order within session or template"
    )
    sets: List["SetCreate"] = Field(
        default_factory=list, description="Sets for this exercise"
    )


class ExerciseSessionUpdate(BaseModel):
    """Schema for updating an existing exercise session."""

    exercise_id: Optional[int] = Field(None)
    session_id: Optional[int] = Field(None)
    template_id: Optional[int] = Field(None)


class ExerciseSessionResponse(ExerciseSessionBase):
    """Schema for exercise session responses."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ExerciseSessionInSession(BaseModel):
    """Exercise session with details for session context."""

    id: int
    exercise_id: int
    order: Optional[int] = None
    exercise: "ExerciseResponse"
    sets: List["SetResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ExerciseSessionInTemplate(BaseModel):
    """Exercise session with details for template context."""

    id: int
    exercise_id: int
    order: Optional[int] = None
    exercise: "ExerciseResponse"
    sets: List["SetResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import for forward reference resolution
from src.schemas.set import SetCreate  # noqa: E402
