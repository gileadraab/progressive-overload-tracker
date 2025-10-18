from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.exercise_session import (
        ExerciseSessionCreate,
        ExerciseSessionInSession,
        ExerciseSessionResponse,
    )


class SessionBase(BaseModel):
    """Base Session schema with common fields."""

    date: Optional[datetime] = Field(None, description="Session date and time")
    notes: Optional[str] = Field(None, description="Workout notes or comments")
    user_id: Optional[int] = Field(
        None, description="ID of the user who owns this session"
    )


class SessionCreate(SessionBase):
    """Schema for creating a new session."""

    user_id: int = Field(..., description="Required user ID for session creation")
    exercise_sessions: List["ExerciseSessionCreate"] = Field(
        default_factory=list, description="Exercise sessions in this workout"
    )


class SessionUpdate(BaseModel):
    """Schema for updating an existing session."""

    date: Optional[datetime] = Field(None)
    notes: Optional[str] = Field(None)
    user_id: Optional[int] = Field(None)


class SetOrderUpdate(BaseModel):
    """Schema for updating a set's order."""

    id: int = Field(..., description="ID of the set to reorder")
    order: int = Field(..., description="New order position")


class ExerciseSessionOrderUpdate(BaseModel):
    """Schema for updating exercise session order and its sets."""

    id: int = Field(..., description="ID of the exercise session to reorder")
    order: Optional[int] = Field(
        None, description="New order position for exercise session"
    )
    sets: Optional[List[SetOrderUpdate]] = Field(
        None, description="Optional set reordering within this exercise"
    )


class SessionReorderRequest(BaseModel):
    """Schema for reordering exercise sessions and sets within a session."""

    exercise_sessions: List[ExerciseSessionOrderUpdate] = Field(
        ..., description="Exercise sessions with new order values"
    )


class SessionResponse(SessionBase):
    """Schema for session responses."""

    id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionWithDetails(SessionResponse):
    """Schema for session with exercise sessions included."""

    exercise_sessions: List["ExerciseSessionInSession"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Import for forward reference resolution
from src.schemas.exercise_session import (  # noqa: E402, F401, F811
    ExerciseSessionCreate,
    ExerciseSessionInSession,
    ExerciseSessionResponse,
)
