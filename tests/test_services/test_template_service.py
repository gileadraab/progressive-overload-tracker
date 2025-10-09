import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.template import Template as TemplateModel
from src.models.user import User
from src.models.exercise import Exercise, CategoryEnum, EquipmentEnum
from src.models.exercise_session import ExerciseSession
from src.schemas.template import TemplateCreate, TemplateUpdate
from src.services import template_service


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(username="testuser", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_exercises(db_session: Session) -> list[Exercise]:
    """Create sample exercises for testing."""
    exercises = [
        Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
        Exercise(name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL),
        Exercise(name="Deadlift", category=CategoryEnum.BACK, equipment=EquipmentEnum.BARBELL),
    ]
    for exercise in exercises:
        db_session.add(exercise)
    db_session.commit()
    for exercise in exercises:
        db_session.refresh(exercise)
    return exercises


class TestGetTemplates:
    """Test suite for get_templates function."""

    def test_get_all_templates(self, db_session: Session, sample_user: User):
        """Test getting all templates."""
        # Create sample templates
        templates = [
            TemplateModel(name="Push Day", user_id=sample_user.id),
            TemplateModel(name="Pull Day", user_id=sample_user.id),
            TemplateModel(name="Leg Day", user_id=sample_user.id),
        ]
        for template in templates:
            db_session.add(template)
        db_session.commit()

        # Get all templates
        result = template_service.get_templates(db_session)
        assert len(result) == 3
        assert result[0].name == "Push Day"
        assert result[1].name == "Pull Day"
        assert result[2].name == "Leg Day"

    def test_get_templates_with_pagination(self, db_session: Session, sample_user: User):
        """Test getting templates with pagination."""
        # Create 5 templates
        for i in range(5):
            template = TemplateModel(name=f"Template {i}", user_id=sample_user.id)
            db_session.add(template)
        db_session.commit()

        # Get first 2 templates
        result = template_service.get_templates(db_session, skip=0, limit=2)
        assert len(result) == 2

        # Get next 2 templates
        result = template_service.get_templates(db_session, skip=2, limit=2)
        assert len(result) == 2

        # Get last template
        result = template_service.get_templates(db_session, skip=4, limit=2)
        assert len(result) == 1

    def test_get_templates_empty_database(self, db_session: Session):
        """Test getting templates from empty database."""
        result = template_service.get_templates(db_session)
        assert result == []

    def test_get_templates_with_nested_exercises(
        self, db_session: Session, sample_user: User, sample_exercises: list[Exercise]
    ):
        """Test that templates are loaded with nested exercise_sessions."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.flush()

        exercise_session = ExerciseSession(
            template_id=template.id,
            exercise_id=sample_exercises[0].id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Get templates and verify nested data is loaded
        result = template_service.get_templates(db_session)
        assert len(result) == 1
        assert len(result[0].exercise_sessions) == 1
        assert result[0].exercise_sessions[0].exercise.name == "Bench Press"


class TestGetTemplate:
    """Test suite for get_template function."""

    def test_get_existing_template(self, db_session: Session, sample_user: User):
        """Test getting an existing template by ID."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        result = template_service.get_template(template.id, db_session)
        assert result.id == template.id
        assert result.name == "Push Day"
        assert result.user_id == sample_user.id

    def test_get_template_with_nested_exercises(
        self, db_session: Session, sample_user: User, sample_exercises: list[Exercise]
    ):
        """Test getting a template with nested exercise sessions."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.flush()

        exercise_session = ExerciseSession(
            template_id=template.id,
            exercise_id=sample_exercises[0].id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Get template and verify nested data
        result = template_service.get_template(template.id, db_session)
        assert len(result.exercise_sessions) == 1
        assert result.exercise_sessions[0].exercise.name == "Bench Press"

    def test_get_nonexistent_template(self, db_session: Session):
        """Test getting a non-existent template raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            template_service.get_template(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestCreateTemplate:
    """Test suite for create_template function."""

    def test_create_template_basic(self, db_session: Session, sample_user: User):
        """Test creating a basic template without exercises."""
        template_data = TemplateCreate(
            name="Push Day",
            user_id=sample_user.id
        )

        result = template_service.create_template(template_data, db_session)
        assert result.id is not None
        assert result.name == "Push Day"
        assert result.user_id == sample_user.id
        assert result.exercise_sessions == []

    def test_create_template_with_exercises(
        self, db_session: Session, sample_user: User, sample_exercises: list[Exercise]
    ):
        """Test creating a template with exercises."""
        template_data = TemplateCreate(
            name="Push Day",
            user_id=sample_user.id,
            exercise_sessions=[
                {"exercise_id": sample_exercises[0].id},
                {"exercise_id": sample_exercises[1].id}
            ]
        )

        result = template_service.create_template(template_data, db_session)
        assert result.id is not None
        assert len(result.exercise_sessions) == 2
        exercise_names = {es.exercise.name for es in result.exercise_sessions}
        assert "Bench Press" in exercise_names
        assert "Squat" in exercise_names

    def test_create_template_with_duplicate_exercises(
        self, db_session: Session, sample_user: User, sample_exercises: list[Exercise]
    ):
        """Test creating a template with duplicate exercise IDs."""
        template_data = TemplateCreate(
            name="Push Day",
            user_id=sample_user.id,
            exercise_sessions=[
                {"exercise_id": sample_exercises[0].id},
                {"exercise_id": sample_exercises[0].id}
            ]
        )

        result = template_service.create_template(template_data, db_session)
        assert len(result.exercise_sessions) == 2
        assert result.exercise_sessions[0].exercise.name == "Bench Press"
        assert result.exercise_sessions[1].exercise.name == "Bench Press"

    def test_create_template_with_nonexistent_exercise(
        self, db_session: Session, sample_user: User
    ):
        """Test creating a template with non-existent exercise ID raises HTTPException."""
        template_data = TemplateCreate(
            name="Push Day",
            user_id=sample_user.id,
            exercise_sessions=[{"exercise_id": 999}]
        )

        with pytest.raises(HTTPException) as exc_info:
            template_service.create_template(template_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_create_template_persisted(self, db_session: Session, sample_user: User):
        """Test that created template is persisted to database."""
        template_data = TemplateCreate(
            name="Push Day",
            user_id=sample_user.id
        )

        created_template = template_service.create_template(template_data, db_session)

        # Verify it's in the database
        retrieved_template = db_session.get(TemplateModel, created_template.id)
        assert retrieved_template is not None
        assert retrieved_template.name == "Push Day"


class TestUpdateTemplate:
    """Test suite for update_template function."""

    def test_update_template_name(self, db_session: Session, sample_user: User):
        """Test updating template name."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        update_data = TemplateUpdate(name="Chest Day")
        result = template_service.update_template(template.id, update_data, db_session)

        assert result.id == template.id
        assert result.name == "Chest Day"
        assert result.user_id == sample_user.id  # Unchanged

    def test_update_template_user(self, db_session: Session, sample_user: User):
        """Test updating template user."""
        # Create another user
        user2 = User(username="testuser2", name="Test User 2")
        db_session.add(user2)
        db_session.commit()

        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        update_data = TemplateUpdate(user_id=user2.id)
        result = template_service.update_template(template.id, update_data, db_session)

        assert result.user_id == user2.id
        assert result.name == "Push Day"  # Unchanged

    def test_update_template_multiple_fields(self, db_session: Session, sample_user: User):
        """Test updating multiple fields at once."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        user2 = User(username="testuser2")
        db_session.add(user2)
        db_session.commit()

        update_data = TemplateUpdate(name="Chest Day", user_id=user2.id)
        result = template_service.update_template(template.id, update_data, db_session)

        assert result.name == "Chest Day"
        assert result.user_id == user2.id

    def test_update_nonexistent_template(self, db_session: Session):
        """Test updating a non-existent template raises HTTPException."""
        update_data = TemplateUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            template_service.update_template(999, update_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_template_partial(self, db_session: Session, sample_user: User):
        """Test partial update with exclude_unset."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        # Only update name, leave user_id unchanged
        update_data = TemplateUpdate(name="Chest Day")
        result = template_service.update_template(template.id, update_data, db_session)

        assert result.name == "Chest Day"
        assert result.user_id == sample_user.id


class TestDeleteTemplate:
    """Test suite for delete_template function."""

    def test_delete_existing_template(self, db_session: Session, sample_user: User):
        """Test deleting an existing template."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()
        template_id = template.id

        # Delete the template
        template_service.delete_template(template_id, db_session)

        # Verify it's deleted
        deleted_template = db_session.get(TemplateModel, template_id)
        assert deleted_template is None

    def test_delete_template_cascades_to_exercise_sessions(
        self, db_session: Session, sample_user: User, sample_exercises: list[Exercise]
    ):
        """Test that deleting a template also deletes related exercise_sessions."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.flush()

        exercise_session = ExerciseSession(
            template_id=template.id,
            exercise_id=sample_exercises[0].id
        )
        db_session.add(exercise_session)
        db_session.commit()

        exercise_session_id = exercise_session.id

        # Delete the template
        template_service.delete_template(template.id, db_session)

        # Verify cascade deletion
        assert db_session.get(ExerciseSession, exercise_session_id) is None

    def test_delete_nonexistent_template(self, db_session: Session):
        """Test deleting a non-existent template raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            template_service.delete_template(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_template_returns_none(self, db_session: Session, sample_user: User):
        """Test that delete_template returns None."""
        template = TemplateModel(name="Push Day", user_id=sample_user.id)
        db_session.add(template)
        db_session.commit()

        result = template_service.delete_template(template.id, db_session)
        assert result is None
