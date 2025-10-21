"""
Authentication dependencies for FastAPI route protection.

Provides dependency functions to extract and validate JWT tokens from requests.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.user import User
from src.services import auth_service

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Extracts the JWT token from the Authorization header, validates it,
    and returns the authenticated user.

    Args:
        credentials: HTTP Bearer token from Authorization header.
        db: Database session dependency.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found.

    Example:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    token = credentials.credentials
    user = auth_service.get_user_from_token(token, db)
    return user
