from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from src.schemas.exercise_session import ExerciseSessionResponse


class TemplateBase(BaseModel):
    """Base Template schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    user_id: Optional[int] = Field(None, description="ID of the user who owns this template")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    user_id: int = Field(..., description="Required user ID for template creation")
    exercise_ids: List[int] = Field(default_factory=list, description="List of exercise IDs to include")


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    user_id: Optional[int] = Field(None)


class TemplateResponse(TemplateBase):
    """Schema for template responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class TemplateWithExerciseSessions(TemplateResponse):
    """Schema for template with exercise sessions included."""
    exercise_sessions: List["ExerciseSessionResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)