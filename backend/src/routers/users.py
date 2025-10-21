from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of users.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific user by ID.

    - **user_id**: The ID of the user to retrieve
    """
    return user_service.get_user(user_id, db)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user.

    - **username**: Unique username (3-50 characters)
    - **name**: Optional display name
    """
    return user_service.create_user(user, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing user.

    Requires authentication. Users can only update their own profile.

    - **user_id**: The ID of the user to update
    - All fields are optional; only provided fields will be updated
    """
    # Ensure user can only update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    return user_service.update_user(user_id, user, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a user.

    Requires authentication. Users can only delete their own account.

    - **user_id**: The ID of the user to delete
    """
    # Ensure user can only delete their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )
    user_service.delete_user(user_id, db)
    return None
