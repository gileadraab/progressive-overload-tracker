from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.exercise_session import (ExerciseSessionCreate,
                                              ExerciseSessionResponse,
                                              ExerciseSessionWithDetails)


class TemplateBase(BaseModel):
    """Base Template schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    user_id: Optional[int] = Field(
        None, description="ID of the user who owns this template"
    )


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""

    user_id: int = Field(..., description="Required user ID for template creation")
    exercise_sessions: List["ExerciseSessionCreate"] = Field(
        default_factory=list, description="Exercise sessions for this template"
    )


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    user_id: Optional[int] = Field(None)
    exercise_sessions: Optional[List["ExerciseSessionCreate"]] = Field(
        None, description="Updated exercise sessions for this template"
    )


class TemplateResponse(TemplateBase):
    """Schema for template responses."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class TemplateWithExerciseSessions(TemplateResponse):
    """Schema for template with exercise sessions included."""

    exercise_sessions: List["ExerciseSessionWithDetails"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import for forward reference resolution
from src.schemas.exercise_session import (  # noqa: E402, F401, F811
    ExerciseSessionCreate,
    ExerciseSessionResponse,
    ExerciseSessionWithDetails,
)
