"""Pytest configuration and fixtures for testing."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import Base first
from src.database.database import Base, get_db
# Import app after models
from src.main import app
from src.models.enums import CategoryEnum, EquipmentEnum, UnitEnum
from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as WorkoutSession
from src.models.set import Set
from src.models.template import Template
# Import all models to ensure they are registered with Base.metadata
from src.models.user import User

# Test database URL (SQLite in-memory with shared cache)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with pooling to share in-memory database."""
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite
        poolclass=StaticPool,  # Share the same connection for in-memory SQLite
        echo=False,  # Set to True to debug SQL
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine
    # Clean up
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with test database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Sample data fixtures


@pytest.fixture
def sample_user(db_session) -> User:
    """Create a sample user for testing."""
    user = User(username="testuser", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_exercise(db_session) -> Exercise:
    """Create a sample exercise for testing."""
    exercise = Exercise(
        name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


@pytest.fixture
def sample_exercise_dumbbell(db_session) -> Exercise:
    """Create a sample dumbbell exercise for testing."""
    exercise = Exercise(
        name="Dumbbell Curl",
        category=CategoryEnum.ARMS,
        equipment=EquipmentEnum.DUMBBELL,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


@pytest.fixture
def sample_session(db_session, sample_user) -> WorkoutSession:
    """Create a sample workout session for testing."""
    session = WorkoutSession(user_id=sample_user.id, notes="Test workout session")
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def sample_template(db_session, sample_user) -> Template:
    """Create a sample template for testing."""
    template = Template(
        user_id=sample_user.id,
        name="Upper Body Day",
        description="Chest and arms workout",
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def sample_exercise_session(
    db_session, sample_session, sample_exercise
) -> ExerciseSession:
    """Create a sample exercise session for testing."""
    exercise_session = ExerciseSession(
        session_id=sample_session.id, exercise_id=sample_exercise.id
    )
    db_session.add(exercise_session)
    db_session.commit()
    db_session.refresh(exercise_session)
    return exercise_session


@pytest.fixture
def sample_set(db_session, sample_session, sample_exercise_session) -> Set:
    """Create a sample set for testing."""
    set_record = Set(
        session_id=sample_session.id,
        exercise_session_id=sample_exercise_session.id,
        weight=100.0,
        reps=10,
        unit=UnitEnum.KG,
    )
    db_session.add(set_record)
    db_session.commit()
    db_session.refresh(set_record)
    return set_record


@pytest.fixture
def sample_workout_with_exercises(
    db_session, sample_user, sample_exercise, sample_exercise_dumbbell
) -> WorkoutSession:
    """Create a complete workout session with exercises and sets."""
    # Create session
    session = WorkoutSession(
        user_id=sample_user.id, notes="Complete workout with exercises and sets"
    )
    db_session.add(session)
    db_session.flush()

    # Add first exercise (Bench Press)
    ex_session_1 = ExerciseSession(
        session_id=session.id, exercise_id=sample_exercise.id
    )
    db_session.add(ex_session_1)
    db_session.flush()

    # Add sets for bench press
    for i in range(3):
        set_record = Set(
            session_id=session.id,
            exercise_session_id=ex_session_1.id,
            weight=100.0 + (i * 10),
            reps=10 - i,
            unit=UnitEnum.KG,
        )
        db_session.add(set_record)

    # Add second exercise (Dumbbell Curl)
    ex_session_2 = ExerciseSession(
        session_id=session.id, exercise_id=sample_exercise_dumbbell.id
    )
    db_session.add(ex_session_2)
    db_session.flush()

    # Add sets for dumbbell curl
    for i in range(3):
        set_record = Set(
            session_id=session.id,
            exercise_session_id=ex_session_2.id,
            weight=15.0 + (i * 2.5),
            reps=12,
            unit=UnitEnum.KG,
        )
        db_session.add(set_record)

    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def multiple_exercises(db_session) -> list[Exercise]:
    """Create multiple exercises for search/filter testing."""
    exercises = [
        Exercise(
            name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
        ),
        Exercise(
            name="Deadlift", category=CategoryEnum.BACK, equipment=EquipmentEnum.BARBELL
        ),
        Exercise(
            name="Overhead Press",
            category=CategoryEnum.SHOULDERS,
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Pull Up",
            category=CategoryEnum.BACK,
            equipment=EquipmentEnum.BODYWEIGHT,
        ),
        Exercise(
            name="Leg Press",
            category=CategoryEnum.LEGS,
            equipment=EquipmentEnum.MACHINE,
        ),
    ]
    for exercise in exercises:
        db_session.add(exercise)
    db_session.commit()
    for exercise in exercises:
        db_session.refresh(exercise)
    return exercises
