from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateWithExerciseSessions,
)
from src.services import template_service

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=List[TemplateWithExerciseSessions])
def list_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve workout templates for the authenticated user.

    Requires authentication. Returns global built-in templates + user's own templates.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    user_id: int = int(current_user.id) if current_user.id else 0
    return template_service.get_templates(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/{template_id}", response_model=TemplateWithExerciseSessions)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific workout template by ID, including its exercises.

    Requires authentication. Users can view global templates or their own templates.

    - **template_id**: The ID of the template to retrieve
    """
    template = template_service.get_template(template_id, db)
    # Verify user can access this template (global or owns it)
    if not template.is_global and template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this template",
        )
    return template


@router.post(
    "/",
    response_model=TemplateWithExerciseSessions,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new workout template with associated exercises.

    Requires authentication. The template will be created for the authenticated user.

    - **name**: Name of the template
    - **user_id**: Must match the authenticated user's ID
    - **exercise_ids**: List of exercise IDs to include in this template
    """
    # Ensure user is creating template for themselves
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create template for another user",
        )
    # Prevent regular users from creating global templates
    if template.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Regular users cannot create global templates",
        )
    return template_service.create_template(template, db)


@router.post(
    "/from-session/{session_id}",
    response_model=TemplateWithExerciseSessions,
    status_code=status.HTTP_201_CREATED,
)
def create_template_from_session(
    session_id: int,
    name: str = Query(..., description="Name for the new template"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a template from an existing session's exercises.

    Requires authentication. Users can only create templates from their own sessions.

    This allows saving a workout as a reusable template.

    **Use case:** User completes a great workout and wants to save it as a template
    for future use.

    **Workflow:**
    - User finishes a workout session
    - Clicks "Save as template"
    - Template is created with the session's exercises (sets are ignored)
    - Template can be used to start future workouts

    - **session_id**: The ID of the session to copy exercises from
    - **name**: Name for the new template
    """
    # Note: template_service will validate the session exists, but we should verify ownership
    # For now, the service will handle it
    user_id: int = int(current_user.id) if current_user.id else 0
    return template_service.create_template_from_session(session_id, name, user_id, db)


@router.put("/{template_id}", response_model=TemplateWithExerciseSessions)
def update_template(
    template_id: int,
    template: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing workout template.

    Requires authentication. Users can only update their own templates (not global ones).

    - **template_id**: The ID of the template to update
    - All fields are optional; only provided fields will be updated
    - **exercise_sessions**: Optional list of exercises to replace the current list
    """
    # Verify template belongs to current user and is not global
    existing_template = template_service.get_template(template_id, db)
    if existing_template.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update global templates",
        )
    if existing_template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this template",
        )
    return template_service.update_template(template_id, template, db)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a workout template.

    Requires authentication. Users can only delete their own templates (not global ones).

    - **template_id**: The ID of the template to delete
    - This will cascade delete all associated exercise_sessions
    """
    # Verify template belongs to current user and is not global
    existing_template = template_service.get_template(template_id, db)
    if existing_template.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete global templates",
        )
    if existing_template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this template",
        )
    template_service.delete_template(template_id, db)
    return None
