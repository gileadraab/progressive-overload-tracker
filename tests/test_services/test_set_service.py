import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.set import Set as SetModel, UnitEnum
from src.models.user import User
from src.models.session import Session as SessionModel
from src.models.exercise import Exercise, CategoryEnum, EquipmentEnum
from src.models.exercise_session import ExerciseSession
from src.schemas.set import SetCreate, SetUpdate
from src.services import set_service


@pytest.fixture
def sample_session(db_session: Session) -> SessionModel:
    """Create a sample session for testing."""
    user = User(username="testuser")
    db_session.add(user)
    db_session.flush()

    session = SessionModel(user_id=user.id, date=datetime.now())
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def sample_exercise_session(db_session: Session, sample_session: SessionModel) -> ExerciseSession:
    """Create a sample exercise session for testing."""
    exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
    db_session.add(exercise)
    db_session.flush()

    exercise_session = ExerciseSession(
        session_id=sample_session.id,
        exercise_id=exercise.id
    )
    db_session.add(exercise_session)
    db_session.commit()
    db_session.refresh(exercise_session)
    return exercise_session


class TestGetSets:
    """Test suite for get_sets function."""

    def test_get_all_sets(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test getting all sets."""
        # Create sample sets
        sets = [
            SetModel(
                exercise_session_id=sample_exercise_session.id,
                weight=100.0,
                reps=10,
                unit=UnitEnum.kg
            ),
            SetModel(
                exercise_session_id=sample_exercise_session.id,
                weight=105.0,
                reps=8,
                unit=UnitEnum.kg
            ),
            SetModel(
                exercise_session_id=sample_exercise_session.id,
                weight=110.0,
                reps=6,
                unit=UnitEnum.kg
            ),
        ]
        for set_item in sets:
            db_session.add(set_item)
        db_session.commit()

        # Get all sets
        result = set_service.get_sets(db_session)
        assert len(result) == 3
        assert result[0].weight == 100.0
        assert result[1].weight == 105.0
        assert result[2].weight == 110.0

    def test_get_sets_with_pagination(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test getting sets with pagination."""
        # Create 5 sets
        for i in range(5):
            set_item = SetModel(
                exercise_session_id=sample_exercise_session.id,
                weight=100.0 + i,
                reps=10,
                unit=UnitEnum.kg
            )
            db_session.add(set_item)
        db_session.commit()

        # Get first 2 sets
        result = set_service.get_sets(db_session, skip=0, limit=2)
        assert len(result) == 2

        # Get next 2 sets
        result = set_service.get_sets(db_session, skip=2, limit=2)
        assert len(result) == 2

        # Get last set
        result = set_service.get_sets(db_session, skip=4, limit=2)
        assert len(result) == 1

    def test_get_sets_empty_database(self, db_session: Session):
        """Test getting sets from empty database."""
        result = set_service.get_sets(db_session)
        assert result == []


class TestGetSet:
    """Test suite for get_set function."""

    def test_get_existing_set(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test getting an existing set by ID."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        result = set_service.get_set(set_item.id, db_session)
        assert result.id == set_item.id
        assert result.weight == 100.0
        assert result.reps == 10
        assert result.unit == UnitEnum.kg

    def test_get_nonexistent_set(self, db_session: Session):
        """Test getting a non-existent set raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            set_service.get_set(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestCreateSet:
    """Test suite for create_set function."""

    def test_create_set_basic(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test creating a basic set."""
        set_data = SetCreate(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )

        result = set_service.create_set(set_data, db_session)
        assert result.id is not None
        assert result.weight == 100.0
        assert result.reps == 10
        assert result.unit == UnitEnum.kg

    def test_create_set_with_stacks_unit(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test creating a set with STACKS unit."""
        set_data = SetCreate(
            exercise_session_id=sample_exercise_session.id,
            weight=5.0,
            reps=12,
            unit=UnitEnum.stacks
        )

        result = set_service.create_set(set_data, db_session)
        assert result.unit == UnitEnum.stacks
        assert result.weight == 5.0

    def test_create_set_persisted(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test that created set is persisted to database."""
        set_data = SetCreate(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )

        created_set = set_service.create_set(set_data, db_session)

        # Verify it's in the database
        retrieved_set = db_session.get(SetModel, created_set.id)
        assert retrieved_set is not None
        assert retrieved_set.weight == 100.0


class TestUpdateSet:
    """Test suite for update_set function."""

    def test_update_set_weight(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test updating set weight."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        update_data = SetUpdate(weight=105.0)
        result = set_service.update_set(set_item.id, update_data, db_session)

        assert result.id == set_item.id
        assert result.weight == 105.0
        assert result.reps == 10  # Unchanged

    def test_update_set_reps(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test updating set reps."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        update_data = SetUpdate(reps=12)
        result = set_service.update_set(set_item.id, update_data, db_session)

        assert result.reps == 12
        assert result.weight == 100.0  # Unchanged

    def test_update_set_unit(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test updating set unit."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        update_data = SetUpdate(unit=UnitEnum.stacks)
        result = set_service.update_set(set_item.id, update_data, db_session)

        assert result.unit == UnitEnum.stacks
        assert result.weight == 100.0  # Unchanged

    def test_update_set_multiple_fields(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test updating multiple fields at once."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        update_data = SetUpdate(weight=110.0, reps=8, unit=UnitEnum.stacks)
        result = set_service.update_set(set_item.id, update_data, db_session)

        assert result.weight == 110.0
        assert result.reps == 8
        assert result.unit == UnitEnum.stacks

    def test_update_nonexistent_set(self, db_session: Session):
        """Test updating a non-existent set raises HTTPException."""
        update_data = SetUpdate(weight=105.0)

        with pytest.raises(HTTPException) as exc_info:
            set_service.update_set(999, update_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_set_partial(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test partial update with exclude_unset."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        # Only update weight, leave other fields unchanged
        update_data = SetUpdate(weight=105.0)
        result = set_service.update_set(set_item.id, update_data, db_session)

        assert result.weight == 105.0
        assert result.reps == 10
        assert result.unit == UnitEnum.kg


class TestDeleteSet:
    """Test suite for delete_set function."""

    def test_delete_existing_set(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test deleting an existing set."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()
        set_id = set_item.id

        # Delete the set
        set_service.delete_set(set_id, db_session)

        # Verify it's deleted
        deleted_set = db_session.get(SetModel, set_id)
        assert deleted_set is None

    def test_delete_nonexistent_set(self, db_session: Session):
        """Test deleting a non-existent set raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            set_service.delete_set(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_set_returns_none(self, db_session: Session, sample_session: SessionModel, sample_exercise_session: ExerciseSession):
        """Test that delete_set returns None."""
        set_item = SetModel(
            exercise_session_id=sample_exercise_session.id,
            weight=100.0,
            reps=10,
            unit=UnitEnum.kg
        )
        db_session.add(set_item)
        db_session.commit()

        result = set_service.delete_set(set_item.id, db_session)
        assert result is None
