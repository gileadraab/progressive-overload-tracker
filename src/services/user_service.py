from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


def get_users(db: DbSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get all users from the database.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of all users.
    """
    result = db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


def get_user(user_id: int, db: DbSession) -> User:
    """
    Get a single user by their ID.

    Args:
        user_id: The ID of the user to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the user with the given ID is not found.

    Returns:
        The retrieved user.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


def get_user_by_username(username: str, db: DbSession) -> User:
    """
    Get a single user by their username.

    Args:
        username: The username of the user to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the user with the given username is not found.

    Returns:
        The retrieved user.
    """
    result = db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found",
        )
    return user


def create_user(user: UserCreate, db: DbSession) -> User:
    """
    Create a new user in the database.

    Args:
        user: The user data to create.
        db: The database session.

    Raises:
        HTTPException: If a user with the same username already exists.

    Returns:
        The newly created user.
    """
    # Check if username already exists
    existing_user = (
        db.execute(select(User).where(User.username == user.username)).scalars().first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' is already taken",
        )

    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(user_id: int, user: UserUpdate, db: DbSession) -> User:
    """
    Update an existing user in the database.

    Args:
        user_id: The ID of the user to update.
        user: The user data to update.
        db: The database session.

    Raises:
        HTTPException: If the user with the given ID is not found or username is taken.

    Returns:
        The updated user.
    """
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    update_data = user.model_dump(exclude_unset=True)

    # Check if username is being updated and if it's already taken
    if "username" in update_data:
        existing_user = (
            db.execute(
                select(User).where(
                    User.username == update_data["username"], User.id != user_id
                )
            )
            .scalars()
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{update_data['username']}' is already taken",
            )

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(user_id: int, db: DbSession) -> None:
    """
    Delete a user from the database.

    Args:
        user_id: The ID of the user to delete.
        db: The database session.

    Raises:
        HTTPException: If the user with the given ID is not found.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    db.delete(user)
    db.commit()
