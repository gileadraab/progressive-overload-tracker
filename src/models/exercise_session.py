from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base


class ExerciseSession(Base):
    __tablename__ = "exercise_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    order = Column(Integer, nullable=True)

    exercise = relationship("Exercise", back_populates="exercise_sessions")
    session = relationship("Session", back_populates="exercise_sessions")
    template = relationship("Template", back_populates="exercise_sessions")
    sets = relationship(
        "Set",
        back_populates="exercise_session",
        cascade="all, delete-orphan",
        order_by="Set.order",
    )
