from typing import List
from sqlalchemy.orm import Session as DbSession
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.set import Set as SetModel
from src.schemas.set import SetCreate, SetUpdate, SetResponse


def get_sets(db: DbSession, skip: int = 0, limit: int = 100) -> List[SetModel]:
    """
    Get all sets from the database.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of all sets.
    """
    result = db.execute(select(SetModel).offset(skip).limit(limit))
    return result.scalars().all()


def get_set(set_id: int, db: DbSession) -> SetModel:
    """
    Get a single set by its ID.

    Args:
        set_id: The ID of the set to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the set with the given ID is not found.

    Returns:
        The retrieved set.
    """
    set_obj = db.get(SetModel, set_id)
    if not set_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Set with id {set_id} not found",
        )
    return set_obj


def create_set(set_data: SetCreate, db: DbSession) -> SetModel:
    """
    Create a new set in the database.

    Args:
        set_data: The set data to create.
        db: The database session.

    Returns:
        The newly created set.
    """
    db_set = SetModel(**set_data.model_dump())
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set


def update_set(set_id: int, set_data: SetUpdate, db: DbSession) -> SetModel:
    """
    Update an existing set in the database.

    Args:
        set_id: The ID of the set to update.
        set_data: The set data to update.
        db: The database session.

    Raises:
        HTTPException: If the set with the given ID is not found.

    Returns:
        The updated set.
    """
    db_set = db.get(SetModel, set_id)
    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Set with id {set_id} not found",
        )

    update_data = set_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_set, field, value)

    db.commit()
    db.refresh(db_set)
    return db_set


def delete_set(set_id: int, db: DbSession) -> None:
    """
    Delete a set from the database.

    Args:
        set_id: The ID of the set to delete.
        db: The database session.

    Raises:
        HTTPException: If the set with the given ID is not found.
    """
    set_obj = db.get(SetModel, set_id)
    if not set_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Set with id {set_id} not found",
        )
    db.delete(set_obj)
    db.commit()
