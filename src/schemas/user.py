from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.session import SessionResponse


class UserBase(BaseModel):
    """Base User schema with common fields."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username for login"
    )
    name: Optional[str] = Field(
        None, max_length=100, description="Optional display name"
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "name": "John Doe",
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Updated username"
    )
    name: Optional[str] = Field(
        None, max_length=100, description="Updated display name"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Johnny Doe",
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user responses."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserWithSessions(UserResponse):
    """Schema for user with sessions included."""

    sessions: List["SessionResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
