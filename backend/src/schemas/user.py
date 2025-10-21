from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    from src.schemas.session import SessionResponse


class UserBase(BaseModel):
    """Base User schema with common fields."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username for login"
    )
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(
        None, max_length=100, description="Optional display name"
    )


class UserCreate(UserBase):
    """Schema for creating a new user (traditional registration)."""

    password: str = Field(..., min_length=8, description="User's password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "name": "John Doe",
                "password": "securepassword123",
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Updated username"
    )
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    name: Optional[str] = Field(
        None, max_length=100, description="Updated display name"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Johnny Doe",
                "email": "johnny@example.com",
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user responses (excludes sensitive data)."""

    id: int
    oauth_provider: Optional[str] = Field(
        None, description="OAuth provider if applicable"
    )

    model_config = ConfigDict(from_attributes=True)


class UserWithSessions(UserResponse):
    """Schema for user with sessions included."""

    sessions: List["SessionResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
