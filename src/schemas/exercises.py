from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from pydantic.config import ConfigDict


class ExerciseBase(BaseModel):
    name_en: str = Field(
        ...,
        json_schema_extra={"example": "Bench Press"}
    )
    name_pt: str = Field(
        ...,
        json_schema_extra={"example": "Supino Reto"}
    )
    category: str = Field(
        ...,
        json_schema_extra={"example": "Chest"}
    )
    subcategory: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Upper Chest"}
    )
    equipment: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Barbell"}
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        json_schema_extra={"example": "https://example.com/images/bench_press.jpg"}
    )


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    equipment: Optional[str] = None
    image_url: Optional[HttpUrl] = None


class ExerciseRead(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
