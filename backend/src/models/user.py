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

    # Authentication fields
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth-only users

    # OAuth fields
    oauth_provider = Column(
        String, nullable=True
    )  # null, "google", "facebook", "instagram"
    oauth_id = Column(String, nullable=True)  # Provider's user ID

    # Relationships
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    templates = relationship(
        "Template", back_populates="user", cascade="all, delete-orphan"
    )
