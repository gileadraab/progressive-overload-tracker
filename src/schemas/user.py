from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    """Base User schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for login")
    name: Optional[str] = Field(None, max_length=100, description="Optional display name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserWithSessions(UserResponse):
    """Schema for user with sessions included."""
    from src.schemas.session import SessionResponse
    sessions: List[SessionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)