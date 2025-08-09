from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.models.enums import EquipmentEnum, CategoryEnum

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)

    category = Column(SqlEnum(CategoryEnum), nullable=False, index=True)
    subcategory = Column(String, nullable=True, index=True)  # Flexible text
    equipment = Column(SqlEnum(EquipmentEnum), nullable=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="exercise")
