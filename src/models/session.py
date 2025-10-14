from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from src.database.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now(), index=True)
    notes = Column(Text, nullable=True)

    # Now properly linked to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    exercise_sessions = relationship(
        "ExerciseSession", back_populates="session", cascade="all, delete-orphan"
    )
