from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.models.enums import CategoryEnum, EquipmentEnum


class ExerciseBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Bench Press"})
    category: CategoryEnum
    subcategory: Optional[str] = Field(
        None, json_schema_extra={"example": "Upper Chest"}
    )
    equipment: Optional[EquipmentEnum] = None
    image_url: Optional[HttpUrl] = Field(
        None,
        json_schema_extra={"example": "https://example.com/images/bench_press.jpg"},
    )


class ExerciseCreate(ExerciseBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Bench Press",
                "category": "chest",
                "subcategory": "Upper Chest",
                "equipment": "barbell",
                "image_url": "https://example.com/images/bench_press.jpg",
            }
        }
    )


class ExerciseUpdate(BaseModel):
    """Schema for updating an existing exercise."""

    name: Optional[str] = Field(None, description="Updated exercise name")
    category: Optional[CategoryEnum] = Field(None, description="Updated category")
    subcategory: Optional[str] = Field(None, description="Updated subcategory")
    equipment: Optional[EquipmentEnum] = Field(None, description="Updated equipment")
    image_url: Optional[HttpUrl] = Field(None, description="Updated image URL")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Incline Bench Press",
                "subcategory": "Upper Chest",
            }
        }
    )


class ExerciseResponse(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility
ExerciseRead = ExerciseResponse


# Exercise History Schemas
class SetSummary(BaseModel):
    """Summary of a single set for history display."""

    weight: float = Field(..., description="Weight used for the set")
    reps: int = Field(..., description="Number of repetitions")
    unit: str = Field(..., description="Unit of measurement (kg or stacks)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"weight": 100.0, "reps": 10, "unit": "kg"}}
    )


class LastPerformed(BaseModel):
    """Details about the most recent session with this exercise."""

    session_id: int = Field(..., description="ID of the most recent session")
    date: str = Field(..., description="Date of the session (ISO format)")
    sets: List[SetSummary] = Field(..., description="Sets performed in that session")
    max_weight: float = Field(..., description="Maximum weight used in the session")
    total_volume: float = Field(..., description="Total volume (weight × reps × sets)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 42,
                "date": "2025-10-15T10:30:00",
                "sets": [
                    {"weight": 100.0, "reps": 10, "unit": "kg"},
                    {"weight": 100.0, "reps": 8, "unit": "kg"},
                    {"weight": 100.0, "reps": 6, "unit": "kg"},
                ],
                "max_weight": 100.0,
                "total_volume": 2400.0,
            }
        }
    )


class PersonalBest(BaseModel):
    """Personal record for this exercise (highest estimated 1RM)."""

    weight: float = Field(..., description="Weight used for the PR set")
    reps: int = Field(..., description="Reps performed for the PR set")
    date: str = Field(..., description="Date of the PR (ISO format)")
    session_id: int = Field(..., description="Session ID where PR was achieved")
    estimated_1rm: float = Field(
        ..., description="Estimated 1-rep max using Brzycki formula"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "weight": 120.0,
                "reps": 5,
                "date": "2025-09-15T14:00:00",
                "session_id": 38,
                "estimated_1rm": 135.0,
            }
        }
    )


class RecentSession(BaseModel):
    """Summary of a recent session with this exercise."""

    session_id: int = Field(..., description="Session ID")
    date: str = Field(..., description="Session date (ISO format)")
    sets: List[SetSummary] = Field(..., description="All sets from that session")
    best_set: SetSummary = Field(
        ..., description="Best set from that session (by volume)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 42,
                "date": "2025-10-15T10:30:00",
                "sets": [
                    {"weight": 100.0, "reps": 10, "unit": "kg"},
                    {"weight": 100.0, "reps": 8, "unit": "kg"},
                ],
                "best_set": {"weight": 100.0, "reps": 10, "unit": "kg"},
            }
        }
    )


class ProgressionSuggestion(BaseModel):
    """Intelligent suggestion for progressive overload."""

    recommended_weight: float = Field(
        ..., description="Suggested weight for next session"
    )
    recommended_reps: int = Field(..., description="Suggested reps for next session")
    rationale: str = Field(..., description="Explanation of the suggestion")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommended_weight": 102.5,
                "recommended_reps": 10,
                "rationale": "You hit target reps - increase weight by 2.5 kg",
            }
        }
    )


class ExerciseHistory(BaseModel):
    """Complete historical performance data for an exercise."""

    exercise_id: int = Field(..., description="ID of the exercise")
    last_performed: Optional[LastPerformed] = Field(
        None, description="Most recent session with this exercise"
    )
    personal_best: Optional[PersonalBest] = Field(
        None, description="Best performance (highest estimated 1RM)"
    )
    recent_sessions: List[RecentSession] = Field(
        default_factory=list, description="Summary of last 5 sessions"
    )
    progression_suggestion: Optional[ProgressionSuggestion] = Field(
        None, description="Recommended weight/reps for progressive overload"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "exercise_id": 5,
                "last_performed": {
                    "session_id": 42,
                    "date": "2025-10-15T10:30:00",
                    "sets": [
                        {"weight": 100.0, "reps": 10, "unit": "kg"},
                        {"weight": 100.0, "reps": 8, "unit": "kg"},
                        {"weight": 100.0, "reps": 6, "unit": "kg"},
                    ],
                    "max_weight": 100.0,
                    "total_volume": 2400.0,
                },
                "personal_best": {
                    "weight": 120.0,
                    "reps": 5,
                    "date": "2025-09-15T14:00:00",
                    "session_id": 38,
                    "estimated_1rm": 135.0,
                },
                "recent_sessions": [
                    {
                        "session_id": 42,
                        "date": "2025-10-15T10:30:00",
                        "sets": [
                            {"weight": 100.0, "reps": 10, "unit": "kg"},
                            {"weight": 100.0, "reps": 8, "unit": "kg"},
                        ],
                        "best_set": {"weight": 100.0, "reps": 10, "unit": "kg"},
                    }
                ],
                "progression_suggestion": {
                    "recommended_weight": 102.5,
                    "recommended_reps": 10,
                    "rationale": "You hit target reps - increase weight by 2.5 kg",
                },
            }
        }
    )
