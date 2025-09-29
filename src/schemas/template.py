from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TemplateBase(BaseModel):
    """Base Template schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class TemplateResponse(TemplateBase):
    """Schema for template responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class TemplateWithExerciseSessions(TemplateResponse):
    """Schema for template with exercise sessions included."""
    from src.schemas.exercise_session import ExerciseSessionResponse

    exercise_sessions: List[ExerciseSessionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)