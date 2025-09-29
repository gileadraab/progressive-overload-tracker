from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SessionBase(BaseModel):
    """Base Session schema with common fields."""
    date: Optional[datetime] = Field(None, description="Session date and time")
    user_id: Optional[int] = Field(None, description="ID of the user who owns this session")


class SessionCreate(SessionBase):
    """Schema for creating a new session."""
    user_id: int = Field(..., description="Required user ID for session creation")


class SessionUpdate(BaseModel):
    """Schema for updating an existing session."""
    date: Optional[datetime] = Field(None)
    user_id: Optional[int] = Field(None)


class SessionResponse(SessionBase):
    """Schema for session responses."""
    id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionWithDetails(SessionResponse):
    """Schema for session with exercise sessions and sets included."""
    from src.schemas.exercise_session import ExerciseSessionResponse
    from src.schemas.set import SetResponse

    exercise_sessions: List[ExerciseSessionResponse] = Field(default_factory=list)
    sets: List[SetResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)