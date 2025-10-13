from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise import CategoryEnum, EquipmentEnum, Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as SessionModel
from src.models.template import Template as TemplateModel
from src.models.user import User
from src.schemas.exercise_session import (ExerciseSessionCreate,
                                          ExerciseSessionUpdate)
from src.services import exercise_session_service


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(username="testuser")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_session(db_session: Session, sample_user: User) -> SessionModel:
    """Create a sample session for testing."""
    session = SessionModel(user_id=sample_user.id, date=datetime.now())
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def sample_template(db_session: Session, sample_user: User) -> TemplateModel:
    """Create a sample template for testing."""
    template = TemplateModel(name="Push Day", user_id=sample_user.id)
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def sample_exercise(db_session: Session) -> Exercise:
    """Create a sample exercise for testing."""
    exercise = Exercise(
        name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


class TestGetExerciseSessions:
    """Test suite for get_exercise_sessions function."""

    def test_get_all_exercise_sessions_from_session(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test getting all exercise sessions from a session."""
        # Create sample exercise sessions
        exercise_sessions = [
            ExerciseSession(
                session_id=sample_session.id, exercise_id=sample_exercise.id
            ),
            ExerciseSession(
                session_id=sample_session.id, exercise_id=sample_exercise.id
            ),
        ]
        for es in exercise_sessions:
            db_session.add(es)
        db_session.commit()

        # Get all exercise sessions
        result = exercise_session_service.get_exercise_sessions(db_session)
        assert len(result) == 2

    def test_get_all_exercise_sessions_from_template(
        self,
        db_session: Session,
        sample_template: TemplateModel,
        sample_exercise: Exercise,
    ):
        """Test getting all exercise sessions from a template."""
        # Create exercise session for template
        exercise_session = ExerciseSession(
            template_id=sample_template.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Get all exercise sessions
        result = exercise_session_service.get_exercise_sessions(db_session)
        assert len(result) == 1
        assert result[0].template_id == sample_template.id

    def test_get_exercise_sessions_with_pagination(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test getting exercise sessions with pagination."""
        # Create 5 exercise sessions
        for i in range(5):
            es = ExerciseSession(
                session_id=sample_session.id, exercise_id=sample_exercise.id
            )
            db_session.add(es)
        db_session.commit()

        # Get first 2
        result = exercise_session_service.get_exercise_sessions(
            db_session, skip=0, limit=2
        )
        assert len(result) == 2

        # Get next 2
        result = exercise_session_service.get_exercise_sessions(
            db_session, skip=2, limit=2
        )
        assert len(result) == 2

        # Get last one
        result = exercise_session_service.get_exercise_sessions(
            db_session, skip=4, limit=2
        )
        assert len(result) == 1

    def test_get_exercise_sessions_empty_database(self, db_session: Session):
        """Test getting exercise sessions from empty database."""
        result = exercise_session_service.get_exercise_sessions(db_session)
        assert result == []

    def test_get_exercise_sessions_with_nested_data(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test that exercise sessions are loaded with nested data."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Get exercise sessions and verify nested data is loaded
        result = exercise_session_service.get_exercise_sessions(db_session)
        assert len(result) == 1
        assert result[0].exercise.name == "Bench Press"
        assert result[0].session.id == sample_session.id


class TestGetExerciseSession:
    """Test suite for get_exercise_session function."""

    def test_get_existing_exercise_session(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test getting an existing exercise session by ID."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        result = exercise_session_service.get_exercise_session(
            exercise_session.id, db_session
        )
        assert result.id == exercise_session.id
        assert result.exercise_id == sample_exercise.id
        assert result.session_id == sample_session.id

    def test_get_exercise_session_with_nested_data(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test getting an exercise session with nested data."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        result = exercise_session_service.get_exercise_session(
            exercise_session.id, db_session
        )
        assert result.exercise.name == "Bench Press"
        assert result.session.id == sample_session.id

    def test_get_nonexistent_exercise_session(self, db_session: Session):
        """Test getting a non-existent exercise session raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            exercise_session_service.get_exercise_session(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestCreateExerciseSession:
    """Test suite for create_exercise_session function."""

    def test_create_exercise_session_for_session(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test creating an exercise session for a workout session."""
        es_data = ExerciseSessionCreate(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )

        result = exercise_session_service.create_exercise_session(es_data, db_session)
        assert result.id is not None
        assert result.session_id == sample_session.id
        assert result.exercise_id == sample_exercise.id
        assert result.template_id is None

    def test_create_exercise_session_for_template(
        self,
        db_session: Session,
        sample_template: TemplateModel,
        sample_exercise: Exercise,
    ):
        """Test creating an exercise session for a template."""
        es_data = ExerciseSessionCreate(
            template_id=sample_template.id, exercise_id=sample_exercise.id
        )

        result = exercise_session_service.create_exercise_session(es_data, db_session)
        assert result.id is not None
        assert result.template_id == sample_template.id
        assert result.exercise_id == sample_exercise.id
        assert result.session_id is None

    def test_create_exercise_session_persisted(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test that created exercise session is persisted to database."""
        es_data = ExerciseSessionCreate(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )

        created_es = exercise_session_service.create_exercise_session(
            es_data, db_session
        )

        # Verify it's in the database
        retrieved_es = db_session.get(ExerciseSession, created_es.id)
        assert retrieved_es is not None
        assert retrieved_es.exercise_id == sample_exercise.id


class TestUpdateExerciseSession:
    """Test suite for update_exercise_session function."""

    def test_update_exercise_session_exercise(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test updating exercise session exercise."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Create another exercise
        exercise2 = Exercise(
            name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
        )
        db_session.add(exercise2)
        db_session.commit()

        update_data = ExerciseSessionUpdate(exercise_id=exercise2.id)
        result = exercise_session_service.update_exercise_session(
            exercise_session.id, update_data, db_session
        )

        assert result.id == exercise_session.id
        assert result.exercise_id == exercise2.id
        assert result.exercise.name == "Squat"

    def test_update_exercise_session_from_session_to_template(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_template: TemplateModel,
        sample_exercise: Exercise,
    ):
        """Test updating exercise session from session to template."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        update_data = ExerciseSessionUpdate(
            template_id=sample_template.id, session_id=None
        )
        result = exercise_session_service.update_exercise_session(
            exercise_session.id, update_data, db_session
        )

        assert result.template_id == sample_template.id
        assert result.session_id is None

    def test_update_nonexistent_exercise_session(
        self, db_session: Session, sample_exercise: Exercise
    ):
        """Test updating a non-existent exercise session raises HTTPException."""
        update_data = ExerciseSessionUpdate(exercise_id=sample_exercise.id)

        with pytest.raises(HTTPException) as exc_info:
            exercise_session_service.update_exercise_session(
                999, update_data, db_session
            )
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_exercise_session_partial(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test partial update with exclude_unset."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        # Create another exercise
        exercise2 = Exercise(
            name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
        )
        db_session.add(exercise2)
        db_session.commit()

        # Only update exercise_id, leave session_id unchanged
        update_data = ExerciseSessionUpdate(exercise_id=exercise2.id)
        result = exercise_session_service.update_exercise_session(
            exercise_session.id, update_data, db_session
        )

        assert result.exercise_id == exercise2.id
        assert result.session_id == sample_session.id


class TestDeleteExerciseSession:
    """Test suite for delete_exercise_session function."""

    def test_delete_existing_exercise_session(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test deleting an existing exercise session."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()
        es_id = exercise_session.id

        # Delete the exercise session
        exercise_session_service.delete_exercise_session(es_id, db_session)

        # Verify it's deleted
        deleted_es = db_session.get(ExerciseSession, es_id)
        assert deleted_es is None

    def test_delete_nonexistent_exercise_session(self, db_session: Session):
        """Test deleting a non-existent exercise session raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            exercise_session_service.delete_exercise_session(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_exercise_session_returns_none(
        self,
        db_session: Session,
        sample_session: SessionModel,
        sample_exercise: Exercise,
    ):
        """Test that delete_exercise_session returns None."""
        exercise_session = ExerciseSession(
            session_id=sample_session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.commit()

        result = exercise_session_service.delete_exercise_session(
            exercise_session.id, db_session
        )
        assert result is None
