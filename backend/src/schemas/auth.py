"""
Authentication schemas for login, token, and OAuth requests/responses.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for email/password login request."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")

    model_config = {
        "json_schema_extra": {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    }


class OAuthLoginRequest(BaseModel):
    """Schema for OAuth login request."""

    provider: str = Field(
        ..., description="OAuth provider (google, facebook, instagram)"
    )
    access_token: str = Field(..., description="OAuth access token from provider")

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "google",
                "access_token": "ya29.a0AfH6SMBx...",
            }
        }
    }


class OAuthUserInfo(BaseModel):
    """Schema for OAuth user information from provider."""

    oauth_id: str = Field(..., description="User ID from OAuth provider")
    email: EmailStr = Field(..., description="User's email from OAuth provider")
    name: Optional[str] = Field(None, description="User's name from OAuth provider")
    username: Optional[str] = Field(None, description="Generated username (from email)")
