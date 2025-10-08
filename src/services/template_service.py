from typing import List, Optional
from sqlalchemy.orm import Session as DbSession, joinedload
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.template import Template as TemplateModel
from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.user import User
from src.schemas.template import TemplateCreate, TemplateUpdate


def get_templates(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
) -> List[TemplateModel]:
    """
    Get all workout templates from the database with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        user_id: Optional user_id filter to get templates for a specific user.

    Returns:
        A list of all templates.
    """
    query = select(TemplateModel).options(
        joinedload(TemplateModel.exercise_sessions).joinedload(
            ExerciseSession.exercise
        ),
        joinedload(TemplateModel.user)
    )

    if user_id:
        query = query.where(TemplateModel.user_id == user_id)

    result = db.execute(query.offset(skip).limit(limit))
    return result.scalars().unique().all()


def get_template(template_id: int, db: DbSession) -> TemplateModel:
    """
    Get a single template by its ID, including its exercises.

    Args:
        template_id: The ID of the template to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.

    Returns:
        The retrieved template.
    """
    result = db.execute(
        select(TemplateModel)
        .options(
            joinedload(TemplateModel.exercise_sessions).joinedload(
                ExerciseSession.exercise
            ),
            joinedload(TemplateModel.user)
        )
        .where(TemplateModel.id == template_id)
    )
    template = result.scalars().first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found",
        )
    return template


def create_template(template_data: TemplateCreate, db: DbSession) -> TemplateModel:
    """
    Create a new template with associated exercises.

    Args:
        template_data: The template data, including exercise sessions.
        db: The database session.

    Raises:
        HTTPException: If user_id or any exercise_id does not exist.

    Returns:
        The newly created template.
    """
    template_dict = template_data.model_dump()

    # Validate user exists
    user = db.get(User, template_dict['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {template_dict['user_id']} not found"
        )

    exercise_sessions_data = template_dict.pop('exercise_sessions', [])

    # Validate all exercises exist
    for es_data in exercise_sessions_data:
        exercise = db.get(Exercise, es_data['exercise_id'])
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {es_data['exercise_id']} not found"
            )

    db_template = TemplateModel(name=template_dict['name'], user_id=template_dict['user_id'])

    # Create exercise sessions for the template
    for es_data in exercise_sessions_data:
        db_exercise_session = ExerciseSession(
            exercise_id=es_data['exercise_id'],
            template_id=None  # Will be set when added to template
        )
        db_template.exercise_sessions.append(db_exercise_session)

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return get_template(db_template.id, db)


def update_template(
    template_id: int, template_data: TemplateUpdate, db: DbSession
) -> TemplateModel:
    """
    Update an existing template.

    Args:
        template_id: The ID of the template to update.
        template_data: The template data to update.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.

    Returns:
        The updated template.
    """
    db_template = db.get(TemplateModel, template_id)
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found",
        )

    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)

    db.commit()
    db.refresh(db_template)
    return get_template(template_id, db)


def delete_template(template_id: int, db: DbSession) -> None:
    """
    Delete a template from the database.

    Args:
        template_id: The ID of the template to delete.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.
    """
    template = db.get(TemplateModel, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found",
        )
    db.delete(template)
    db.commit()
