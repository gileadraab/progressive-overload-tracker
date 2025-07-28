from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    exercise_sessions = relationship("ExerciseSession", back_populates="template")
