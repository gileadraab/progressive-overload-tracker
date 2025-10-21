"""
Authentication router for user registration, login, and token management.

Provides endpoints for email/password authentication, OAuth, and token refresh.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.user import User
from src.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from src.schemas.user import UserCreate, UserResponse
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.

    Creates a new user account with hashed password. Username and email must be unique.

    Args:
        user_data: User registration data including username, email, name, and password.
        db: Database session dependency.

    Returns:
        UserResponse: The newly created user (without password).

    Raises:
        HTTPException 400: If username or email already exists.
    """
    user = auth_service.register_user(user_data, db)
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Authenticates user credentials and returns access and refresh tokens.

    Args:
        credentials: Login credentials (email and password).
        db: Database session dependency.

    Returns:
        TokenResponse: Access token, refresh token, and token type.

    Raises:
        HTTPException 401: If credentials are invalid.
    """
    user = auth_service.authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens with user ID as subject
    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Validates the refresh token and issues a new access token.

    Args:
        request: Refresh token request containing the refresh token.
        db: Database session dependency.

    Returns:
        TokenResponse: New access token and the same refresh token.

    Raises:
        HTTPException 401: If refresh token is invalid or expired.
    """
    # Verify refresh token
    payload = auth_service.verify_token(request.refresh_token, expected_type="refresh")
    user_id_raw = payload.get("sub")

    # Validate user_id is present and is an integer
    if user_id_raw is None or not isinstance(user_id_raw, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id: int = user_id_raw

    # Verify user still exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new access token
    access_token = auth_service.create_access_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
    )


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal).

    Since JWT tokens are stateless, logout is handled client-side by removing tokens.
    This endpoint exists for API consistency and future token blacklisting.

    Returns:
        Success message.
    """
    return {"message": "Successfully logged out. Please remove tokens from client."}
