from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.models.enums import CategoryEnum, EquipmentEnum


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)

    category = Column(SqlEnum(CategoryEnum), nullable=False, index=True)
    subcategory = Column(String, nullable=True, index=True)  # Flexible text
    equipment = Column(SqlEnum(EquipmentEnum), nullable=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="exercise")
