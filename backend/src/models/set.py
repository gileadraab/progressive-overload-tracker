from sqlalchemy import Column, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.models.enums import UnitEnum


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    unit = Column(Enum(UnitEnum), nullable=False)
    exercise_session_id = Column(
        Integer, ForeignKey("exercise_sessions.id"), nullable=False
    )
    order = Column(Integer, nullable=True)

    exercise_session = relationship("ExerciseSession", back_populates="sets")
