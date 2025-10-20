from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise import CategoryEnum, EquipmentEnum, Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as SessionModel
from src.models.set import Set as SetModel
from src.models.set import UnitEnum
from src.models.user import User
from src.schemas.exercise_session import ExerciseSessionCreate
from src.schemas.session import SessionCreate, SessionUpdate
from src.schemas.set import SetCreate
from src.services import session_service


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(username="testuser", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


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


class TestGetSessions:
    """Test suite for get_sessions function."""

    def test_get_all_sessions(self, db_session: Session, sample_user: User):
        """Test getting all sessions."""
        # Create sample sessions
        sessions = [
            SessionModel(user_id=sample_user.id, date=datetime.now()),
            SessionModel(user_id=sample_user.id, date=datetime.now()),
            SessionModel(user_id=sample_user.id, date=datetime.now()),
        ]
        for session in sessions:
            db_session.add(session)
        db_session.commit()

        # Get all sessions
        result = session_service.get_sessions(db_session)
        assert len(result) == 3

    def test_get_sessions_with_pagination(self, db_session: Session, sample_user: User):
        """Test getting sessions with pagination."""
        # Create 5 sessions
        for i in range(5):
            session = SessionModel(user_id=sample_user.id, date=datetime.now())
            db_session.add(session)
        db_session.commit()

        # Get first 2 sessions
        result = session_service.get_sessions(db_session, skip=0, limit=2)
        assert len(result) == 2

        # Get next 2 sessions
        result = session_service.get_sessions(db_session, skip=2, limit=2)
        assert len(result) == 2

        # Get last session
        result = session_service.get_sessions(db_session, skip=4, limit=2)
        assert len(result) == 1

    def test_get_sessions_empty_database(self, db_session: Session):
        """Test getting sessions from empty database."""
        result = session_service.get_sessions(db_session)
        assert result == []

    def test_get_sessions_with_nested_data(
        self, db_session: Session, sample_user: User, sample_exercise: Exercise
    ):
        """Test that sessions are loaded with nested exercise_sessions and sets."""
        # Create session with nested data
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.flush()

        exercise_session = ExerciseSession(
            session_id=session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.flush()

        set_item = SetModel(
            exercise_session_id=exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg,
        )
        db_session.add(set_item)
        db_session.commit()

        # Get sessions and verify nested data is loaded
        result = session_service.get_sessions(db_session)
        assert len(result) == 1
        assert len(result[0].exercise_sessions) == 1
        assert result[0].exercise_sessions[0].exercise.name == "Bench Press"
        assert len(result[0].exercise_sessions[0].sets) == 1


class TestGetSession:
    """Test suite for get_session function."""

    def test_get_existing_session(self, db_session: Session, sample_user: User):
        """Test getting an existing session by ID."""
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.commit()

        result = session_service.get_session(session.id, db_session)
        assert result.id == session.id
        assert result.user_id == sample_user.id

    def test_get_session_with_nested_data(
        self, db_session: Session, sample_user: User, sample_exercise: Exercise
    ):
        """Test getting a session with nested exercise sessions and sets."""
        # Create session with nested data
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.flush()

        exercise_session = ExerciseSession(
            session_id=session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.flush()

        set_item = SetModel(
            exercise_session_id=exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg,
        )
        db_session.add(set_item)
        db_session.commit()

        # Get session and verify nested data
        result = session_service.get_session(session.id, db_session)
        assert len(result.exercise_sessions) == 1
        assert result.exercise_sessions[0].exercise.name == "Bench Press"
        assert len(result.exercise_sessions[0].sets) == 1
        assert result.exercise_sessions[0].sets[0].weight == 100.0

    def test_get_nonexistent_session(self, db_session: Session):
        """Test getting a non-existent session raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            session_service.get_session(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestCreateSession:
    """Test suite for create_session function."""

    def test_create_session_basic(self, db_session: Session, sample_user: User):
        """Test creating a basic session without exercises."""
        session_data = SessionCreate(user_id=sample_user.id, date=datetime.now())

        result = session_service.create_session(session_data, db_session)
        assert result.id is not None
        assert result.user_id == sample_user.id
        assert result.exercise_sessions == []

    def test_create_session_with_exercises_and_sets(
        self, db_session: Session, sample_user: User, sample_exercise: Exercise
    ):
        """Test creating a session with nested exercises and sets."""
        session_data = SessionCreate(
            user_id=sample_user.id,
            date=datetime.now(),
            exercise_sessions=[
                ExerciseSessionCreate(
                    exercise_id=sample_exercise.id,
                    sets=[
                        SetCreate(weight=100.0, reps=10, unit=UnitEnum.kg),
                        SetCreate(weight=105.0, reps=8, unit=UnitEnum.kg),
                    ],
                )
            ],
        )

        result = session_service.create_session(session_data, db_session)
        assert result.id is not None
        assert len(result.exercise_sessions) == 1
        assert result.exercise_sessions[0].exercise_id == sample_exercise.id
        assert len(result.exercise_sessions[0].sets) == 2
        assert result.exercise_sessions[0].sets[0].weight == 100.0
        assert result.exercise_sessions[0].sets[1].weight == 105.0

    def test_create_session_multiple_exercises(
        self, db_session: Session, sample_user: User
    ):
        """Test creating a session with multiple exercises."""
        # Create additional exercises
        exercise1 = Exercise(
            name="Bench Press",
            category=CategoryEnum.CHEST,
            equipment=EquipmentEnum.BARBELL,
        )
        exercise2 = Exercise(
            name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
        )
        db_session.add_all([exercise1, exercise2])
        db_session.commit()

        session_data = SessionCreate(
            user_id=sample_user.id,
            date=datetime.now(),
            exercise_sessions=[
                ExerciseSessionCreate(
                    exercise_id=exercise1.id,
                    sets=[SetCreate(weight=100.0, reps=10, unit=UnitEnum.kg)],
                ),
                ExerciseSessionCreate(
                    exercise_id=exercise2.id,
                    sets=[SetCreate(weight=150.0, reps=5, unit=UnitEnum.kg)],
                ),
            ],
        )

        result = session_service.create_session(session_data, db_session)
        assert len(result.exercise_sessions) == 2
        assert result.exercise_sessions[0].exercise.name == "Bench Press"
        assert result.exercise_sessions[1].exercise.name == "Squat"

    def test_create_session_persisted(self, db_session: Session, sample_user: User):
        """Test that created session is persisted to database."""
        session_data = SessionCreate(user_id=sample_user.id, date=datetime.now())

        created_session = session_service.create_session(session_data, db_session)

        # Verify it's in the database
        retrieved_session = db_session.get(SessionModel, created_session.id)
        assert retrieved_session is not None
        assert retrieved_session.user_id == sample_user.id


class TestUpdateSession:
    """Test suite for update_session function."""

    def test_update_session_date(self, db_session: Session, sample_user: User):
        """Test updating session date."""
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.commit()

        new_date = datetime(2024, 1, 1, 12, 0, 0)
        update_data = SessionUpdate(date=new_date)
        result = session_service.update_session(session.id, update_data, db_session)

        assert result.id == session.id
        assert result.date == new_date

    def test_update_session_user(self, db_session: Session, sample_user: User):
        """Test updating session user."""
        # Create another user
        user2 = User(username="testuser2", name="Test User 2")
        db_session.add(user2)
        db_session.commit()

        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.commit()

        update_data = SessionUpdate(user_id=user2.id)
        result = session_service.update_session(session.id, update_data, db_session)

        assert result.user_id == user2.id

    def test_update_nonexistent_session(self, db_session: Session):
        """Test updating a non-existent session raises HTTPException."""
        update_data = SessionUpdate(date=datetime.now())

        with pytest.raises(HTTPException) as exc_info:
            session_service.update_session(999, update_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_session_partial(self, db_session: Session, sample_user: User):
        """Test partial update with exclude_unset."""
        original_date = datetime.now()
        session = SessionModel(user_id=sample_user.id, date=original_date)
        db_session.add(session)
        db_session.commit()

        # Only update user_id, leave date unchanged
        user2 = User(username="testuser2")
        db_session.add(user2)
        db_session.commit()

        update_data = SessionUpdate(user_id=user2.id)
        result = session_service.update_session(session.id, update_data, db_session)

        assert result.user_id == user2.id
        assert result.date == original_date


class TestDeleteSession:
    """Test suite for delete_session function."""

    def test_delete_existing_session(self, db_session: Session, sample_user: User):
        """Test deleting an existing session."""
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.commit()
        session_id = session.id

        # Delete the session
        session_service.delete_session(session_id, db_session)

        # Verify it's deleted
        deleted_session = db_session.get(SessionModel, session_id)
        assert deleted_session is None

    def test_delete_session_cascades_to_exercise_sessions(
        self, db_session: Session, sample_user: User, sample_exercise: Exercise
    ):
        """Test that deleting a session also deletes related exercise_sessions and sets."""
        # Create session with nested data
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.flush()

        exercise_session = ExerciseSession(
            session_id=session.id, exercise_id=sample_exercise.id
        )
        db_session.add(exercise_session)
        db_session.flush()

        set_item = SetModel(
            exercise_session_id=exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg,
        )
        db_session.add(set_item)
        db_session.commit()

        exercise_session_id = exercise_session.id
        set_id = set_item.id

        # Delete the session
        session_service.delete_session(session.id, db_session)

        # Verify cascade deletion
        assert db_session.get(ExerciseSession, exercise_session_id) is None
        assert db_session.get(SetModel, set_id) is None

    def test_delete_nonexistent_session(self, db_session: Session):
        """Test deleting a non-existent session raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            session_service.delete_session(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_session_returns_none(self, db_session: Session, sample_user: User):
        """Test that delete_session returns None."""
        session = SessionModel(user_id=sample_user.id, date=datetime.now())
        db_session.add(session)
        db_session.commit()

        result = session_service.delete_session(session.id, db_session)
        assert result is None
