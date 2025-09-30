from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from src.models.enums import EquipmentEnum, CategoryEnum


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
