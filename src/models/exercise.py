from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String, nullable=False, index=True)
    name_pt = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True, index=True)
    equipment = Column(String, nullable=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="exercise")
