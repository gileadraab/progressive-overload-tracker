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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 1,
                "date": "2025-10-19T10:30:00",
                "notes": "Great chest and triceps workout!",
                "exercise_sessions": [
                    {
                        "exercise_id": 5,
                        "sets": [
                            {"weight": 100.0, "reps": 10, "unit": "kg"},
                            {"weight": 100.0, "reps": 8, "unit": "kg"},
                            {"weight": 100.0, "reps": 6, "unit": "kg"},
                        ],
                    },
                    {
                        "exercise_id": 12,
                        "sets": [
                            {"weight": 30.0, "reps": 12, "unit": "kg"},
                            {"weight": 30.0, "reps": 10, "unit": "kg"},
                        ],
                    },
                ],
            }
        }
    )


class SessionUpdate(BaseModel):
    """Schema for updating an existing session with full replacement.

    This allows complete editing of sessions - users can modify exercises, sets,
    weights, reps, notes, and date. The update is a full replacement: all existing
    exercise_sessions and sets are deleted and replaced with the provided data.

    This enables workflows like:
    - Fixing typos in weights (e.g., 1000kg -> 100kg)
    - Adding forgotten exercises
    - Removing incorrect sets
    - Correcting historical data
    """

    date: Optional[datetime] = Field(None, description="Updated session date/time")
    notes: Optional[str] = Field(None, description="Updated notes or comments")
    exercise_sessions: Optional[List["ExerciseSessionCreate"]] = Field(
        None, description="Complete replacement of exercise sessions and sets"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-10-19T10:30:00",
                "notes": "Amazing workout! Hit new PR on bench press!",
                "exercise_sessions": [
                    {
                        "exercise_id": 5,
                        "sets": [
                            {"weight": 100.0, "reps": 10, "unit": "kg"},
                            {"weight": 100.0, "reps": 8, "unit": "kg"},
                        ],
                    },
                    {
                        "exercise_id": 12,
                        "sets": [
                            {"weight": 30.0, "reps": 12, "unit": "kg"},
                        ],
                    },
                ],
            }
        }
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
