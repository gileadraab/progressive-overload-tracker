from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import joinedload

from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as SessionModel
from src.models.template import Template as TemplateModel
from src.models.user import User
from src.schemas.exercise_session import ExerciseSessionCreate
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
        joinedload(TemplateModel.exercise_sessions)
        .joinedload(ExerciseSession.exercise),
        joinedload(TemplateModel.exercise_sessions)
        .joinedload(ExerciseSession.sets),
        joinedload(TemplateModel.user),
    )

    if user_id:
        query = query.where(TemplateModel.user_id == user_id)

    result = db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().unique().all())


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
            joinedload(TemplateModel.exercise_sessions)
            .joinedload(ExerciseSession.exercise),
            joinedload(TemplateModel.exercise_sessions)
            .joinedload(ExerciseSession.sets),
            joinedload(TemplateModel.user),
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
    user = db.get(User, template_dict["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {template_dict['user_id']} not found",
        )

    exercise_sessions_data = template_dict.pop("exercise_sessions", [])

    # Validate all exercises exist
    for es_data in exercise_sessions_data:
        exercise = db.get(Exercise, es_data["exercise_id"])
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {es_data['exercise_id']} not found",
            )

    db_template = TemplateModel(
        name=template_dict["name"], user_id=template_dict["user_id"]
    )

    # Create exercise sessions for the template
    for es_index, es_data in enumerate(exercise_sessions_data, start=1):
        # Assign order based on position if not provided
        order = es_data.get("order", es_index)
        db_exercise_session = ExerciseSession(
            exercise_id=es_data["exercise_id"],
            template_id=None,  # Will be set when added to template
            order=order,
        )
        db_template.exercise_sessions.append(db_exercise_session)

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return get_template(int(db_template.id), db)


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
        HTTPException: If any exercise_id does not exist.

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

    # Handle exercise_sessions update if provided
    if "exercise_sessions" in update_data:
        exercise_sessions_data = update_data.pop("exercise_sessions")

        # Validate all exercises exist
        for es_data in exercise_sessions_data:
            exercise = db.get(Exercise, es_data["exercise_id"])
            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Exercise with id {es_data['exercise_id']} not found",
                )

        # Clear existing exercise_sessions
        db_template.exercise_sessions = []

        # Add new exercise_sessions
        for es_index, es_data in enumerate(exercise_sessions_data, start=1):
            # Assign order based on position if not provided
            order = es_data.get("order", es_index)
            db_exercise_session = ExerciseSession(
                exercise_id=es_data["exercise_id"],
                template_id=None,  # Will be set when added to template
                order=order,
            )
            db_template.exercise_sessions.append(db_exercise_session)

    # Update other fields (name, user_id)
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


def get_template_as_session(
    template_id: int, user_id: int, db: DbSession
) -> Dict[str, Any]:
    """
    Get a template structure suitable for creating a new session.
    Returns data in SessionCreate format with exercises (no sets).

    Args:
        template_id: The ID of the template to use as base.
        user_id: The ID of the user for the new session.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.
        HTTPException: If the user with the given ID is not found.

    Returns:
        A dictionary in SessionCreate format with exercises from the template.
    """
    # Validate user exists
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Get template with exercises
    template = get_template(template_id, db)

    # Build session structure from template
    return {
        "user_id": user_id,
        "date": None,  # Will default to now when creating session
        "exercise_sessions": [
            {
                "exercise_id": es.exercise_id,
                "order": es.order,
                "sets": [],  # Template has no sets - user fills during workout
            }
            for es in template.exercise_sessions
        ],
    }


def create_template_from_session(
    session_id: int, name: str, user_id: int, db: DbSession
) -> TemplateModel:
    """
    Create a template from an existing session's exercise list.
    Saves a workout as a reusable template.

    Args:
        session_id: The ID of the session to copy exercises from.
        name: The name for the new template.
        user_id: The ID of the user who owns the template.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.
        HTTPException: If the user with the given ID is not found.

    Returns:
        The newly created template.
    """
    # Validate user exists
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Get session with exercises
    result = db.execute(
        select(SessionModel)
        .options(
            joinedload(SessionModel.exercise_sessions).joinedload(
                ExerciseSession.exercise
            )
        )
        .where(SessionModel.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )

    # Create template with exercises (ignore sets from session)
    template_data = TemplateCreate(
        user_id=user_id,
        name=name,
        exercise_sessions=[
            ExerciseSessionCreate(
                exercise_id=es.exercise_id,
                session_id=None,
                template_id=None,
                order=es.order,
                sets=[],
            )
            for es in session.exercise_sessions
        ],
    )

    return create_template(template_data, db)
