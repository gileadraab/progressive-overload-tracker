from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from src.models.enums import EquipmentEnum, CategoryEnum, UnitEnum


class ExerciseBase(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra={"example": "Bench Press"}
    )
    category: CategoryEnum
    subcategory: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Upper Chest"}
    )
    equipment: Optional[EquipmentEnum] = None
    image_url: Optional[HttpUrl] = Field(
        None,
        json_schema_extra={"example": "https://example.com/images/bench_press.jpg"}
    )


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[CategoryEnum] = None
    subcategory: Optional[str] = None
    equipment: Optional[EquipmentEnum] = None
    image_url: Optional[HttpUrl] = None


class ExerciseResponse(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility
ExerciseRead = ExerciseResponse


# Exercise History Schemas
class SetSummary(BaseModel):
    weight: float
    reps: int
    unit: str


class LastPerformed(BaseModel):
    session_id: int
    date: str
    sets: List[SetSummary]
    max_weight: float
    total_volume: float


class PersonalBest(BaseModel):
    weight: float
    reps: int
    date: str
    session_id: int
    estimated_1rm: float


class RecentSession(BaseModel):
    session_id: int
    date: str
    sets: List[SetSummary]
    best_set: SetSummary


class ProgressionSuggestion(BaseModel):
    recommended_weight: float
    recommended_reps: int
    rationale: str


class ExerciseHistory(BaseModel):
    exercise_id: int
    last_performed: Optional[LastPerformed] = None
    personal_best: Optional[PersonalBest] = None
    recent_sessions: List[RecentSession] = []
    progression_suggestion: Optional[ProgressionSuggestion] = None
