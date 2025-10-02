from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.template import TemplateCreate, TemplateUpdate, TemplateWithExerciseSessions
from src.services import template_service

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=List[TemplateWithExerciseSessions])
def list_templates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of workout templates with their exercises.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    return template_service.get_templates(db, skip=skip, limit=limit)


@router.get("/{template_id}", response_model=TemplateWithExerciseSessions)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific workout template by ID, including its exercises.

    - **template_id**: The ID of the template to retrieve
    """
    return template_service.get_template(template_id, db)


@router.post("/", response_model=TemplateWithExerciseSessions, status_code=status.HTTP_201_CREATED)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new workout template with associated exercises.

    - **name**: Name of the template
    - **user_id**: ID of the user who owns this template
    - **exercise_ids**: List of exercise IDs to include in this template
    """
    return template_service.create_template(template, db)


@router.put("/{template_id}", response_model=TemplateWithExerciseSessions)
def update_template(
    template_id: int,
    template: TemplateUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing workout template.

    - **template_id**: The ID of the template to update
    - All fields are optional; only provided fields will be updated
    - Note: This endpoint updates template metadata only, not associated exercises
    """
    return template_service.update_template(template_id, template, db)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a workout template.

    - **template_id**: The ID of the template to delete
    - This will cascade delete all associated exercise_sessions
    """
    template_service.delete_template(template_id, db)
    return None
