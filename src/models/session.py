from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import relationship

from src.database.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now(), index=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="session")
