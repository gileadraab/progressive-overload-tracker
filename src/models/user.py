from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Unique login/identifier
    username = Column(String, unique=True, index=True, nullable=False)

    # Friendly display name (not unique)
    name = Column(String, nullable=True)

    # Relationships
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    templates = relationship(
        "Template", back_populates="user", cascade="all, delete-orphan"
    )
