import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise import Exercise, CategoryEnum, EquipmentEnum
from src.schemas.exercise import ExerciseCreate, ExerciseUpdate
from src.services import exercise_service


class TestGetExercises:
    """Test suite for get_exercises function."""

    def test_get_all_exercises(self, db_session: Session):
        """Test getting all exercises."""
        # Create sample exercises
        exercises = [
            Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
            Exercise(name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL),
            Exercise(name="Deadlift", category=CategoryEnum.BACK, equipment=EquipmentEnum.BARBELL),
        ]
        for exercise in exercises:
            db_session.add(exercise)
        db_session.commit()

        # Get all exercises
        result = exercise_service.get_exercises(db_session)
        assert len(result) == 3
        assert result[0].name == "Bench Press"
        assert result[1].name == "Squat"
        assert result[2].name == "Deadlift"

    def test_get_exercises_with_pagination(self, db_session: Session):
        """Test getting exercises with pagination."""
        # Create 5 exercises
        for i in range(5):
            exercise = Exercise(
                name=f"Exercise {i}",
                category=CategoryEnum.CHEST,
                equipment=EquipmentEnum.DUMBBELL
            )
            db_session.add(exercise)
        db_session.commit()

        # Get first 2 exercises
        result = exercise_service.get_exercises(db_session, skip=0, limit=2)
        assert len(result) == 2

        # Get next 2 exercises
        result = exercise_service.get_exercises(db_session, skip=2, limit=2)
        assert len(result) == 2

        # Get last exercise
        result = exercise_service.get_exercises(db_session, skip=4, limit=2)
        assert len(result) == 1

    def test_get_exercises_empty_database(self, db_session: Session):
        """Test getting exercises from empty database."""
        result = exercise_service.get_exercises(db_session)
        assert result == []


class TestSearchExercises:
    """Test suite for search_exercises function."""

    def test_search_by_name(self, db_session: Session):
        """Test searching exercises by name."""
        exercises = [
            Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
            Exercise(name="Incline Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
            Exercise(name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL),
        ]
        for exercise in exercises:
            db_session.add(exercise)
        db_session.commit()

        # Search for "bench"
        result = exercise_service.search_exercises("bench", db_session)
        assert len(result) == 2
        assert all("bench" in ex.name.lower() for ex in result)

    def test_search_by_category(self, db_session: Session):
        """Test searching exercises by category."""
        exercises = [
            Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
            Exercise(name="Push Up", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BODYWEIGHT),
            Exercise(name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL),
        ]
        for exercise in exercises:
            db_session.add(exercise)
        db_session.commit()

        # Search for "chest"
        result = exercise_service.search_exercises("chest", db_session)
        assert len(result) == 2
        assert all(ex.category == CategoryEnum.CHEST for ex in result)

    def test_search_by_subcategory(self, db_session: Session):
        """Test searching exercises by subcategory."""
        exercises = [
            Exercise(
                name="Cable Fly",
                category=CategoryEnum.CHEST,
                equipment=EquipmentEnum.MACHINE,
                subcategory="Upper Chest"
            ),
            Exercise(
                name="Incline Press",
                category=CategoryEnum.CHEST,
                equipment=EquipmentEnum.BARBELL,
                subcategory="Upper Chest"
            ),
            Exercise(name="Flat Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL),
        ]
        for exercise in exercises:
            db_session.add(exercise)
        db_session.commit()

        # Search for "upper"
        result = exercise_service.search_exercises("upper", db_session)
        assert len(result) == 2
        assert all("upper" in (ex.subcategory or "").lower() for ex in result)

    def test_search_case_insensitive(self, db_session: Session):
        """Test that search is case-insensitive."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        # Test different case variations
        for query in ["bench", "BENCH", "Bench", "bEnCh"]:
            result = exercise_service.search_exercises(query, db_session)
            assert len(result) == 1
            assert result[0].name == "Bench Press"

    def test_search_no_results(self, db_session: Session):
        """Test searching with no matching results."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        result = exercise_service.search_exercises("nonexistent", db_session)
        assert result == []


class TestGetExercise:
    """Test suite for get_exercise function."""

    def test_get_existing_exercise(self, db_session: Session):
        """Test getting an existing exercise by ID."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        result = exercise_service.get_exercise(exercise.id, db_session)
        assert result.id == exercise.id
        assert result.name == "Bench Press"
        assert result.category == CategoryEnum.CHEST

    def test_get_nonexistent_exercise(self, db_session: Session):
        """Test getting a non-existent exercise raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            exercise_service.get_exercise(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestCreateExercise:
    """Test suite for create_exercise function."""

    def test_create_exercise_basic(self, db_session: Session):
        """Test creating a basic exercise."""
        exercise_data = ExerciseCreate(
            name="Bench Press",
            category=CategoryEnum.CHEST,
            equipment=EquipmentEnum.BARBELL
        )

        result = exercise_service.create_exercise(exercise_data, db_session)
        assert result.id is not None
        assert result.name == "Bench Press"
        assert result.category == CategoryEnum.CHEST
        assert result.equipment == EquipmentEnum.BARBELL
        assert result.subcategory is None

    def test_create_exercise_with_subcategory(self, db_session: Session):
        """Test creating an exercise with subcategory."""
        exercise_data = ExerciseCreate(
            name="Incline Bench Press",
            category=CategoryEnum.CHEST,
            equipment=EquipmentEnum.BARBELL,
            subcategory="Upper Chest"
        )

        result = exercise_service.create_exercise(exercise_data, db_session)
        assert result.id is not None
        assert result.name == "Incline Bench Press"
        assert result.subcategory == "Upper Chest"

    def test_create_exercise_persisted(self, db_session: Session):
        """Test that created exercise is persisted to database."""
        exercise_data = ExerciseCreate(
            name="Squat",
            category=CategoryEnum.LEGS,
            equipment=EquipmentEnum.BARBELL
        )

        created_exercise = exercise_service.create_exercise(exercise_data, db_session)

        # Verify it's in the database
        retrieved_exercise = db_session.get(Exercise, created_exercise.id)
        assert retrieved_exercise is not None
        assert retrieved_exercise.name == "Squat"


class TestUpdateExercise:
    """Test suite for update_exercise function."""

    def test_update_exercise_name(self, db_session: Session):
        """Test updating exercise name."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        update_data = ExerciseUpdate(name="Incline Bench Press")
        result = exercise_service.update_exercise(exercise.id, update_data, db_session)

        assert result.id == exercise.id
        assert result.name == "Incline Bench Press"
        assert result.category == CategoryEnum.CHEST  # Unchanged

    def test_update_exercise_category(self, db_session: Session):
        """Test updating exercise category."""
        exercise = Exercise(name="Pull Up", category=CategoryEnum.BACK, equipment=EquipmentEnum.BODYWEIGHT)
        db_session.add(exercise)
        db_session.commit()

        update_data = ExerciseUpdate(category=CategoryEnum.ARMS)
        result = exercise_service.update_exercise(exercise.id, update_data, db_session)

        assert result.id == exercise.id
        assert result.category == CategoryEnum.ARMS
        assert result.name == "Pull Up"  # Unchanged

    def test_update_exercise_multiple_fields(self, db_session: Session):
        """Test updating multiple fields at once."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        update_data = ExerciseUpdate(
            name="Dumbbell Press",
            equipment=EquipmentEnum.DUMBBELL,
            subcategory="Upper Chest"
        )
        result = exercise_service.update_exercise(exercise.id, update_data, db_session)

        assert result.name == "Dumbbell Press"
        assert result.equipment == EquipmentEnum.DUMBBELL
        assert result.subcategory == "Upper Chest"
        assert result.category == CategoryEnum.CHEST  # Unchanged

    def test_update_nonexistent_exercise(self, db_session: Session):
        """Test updating a non-existent exercise raises HTTPException."""
        update_data = ExerciseUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            exercise_service.update_exercise(999, update_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_exercise_partial(self, db_session: Session):
        """Test partial update with exclude_unset."""
        exercise = Exercise(
            name="Bench Press",
            category=CategoryEnum.CHEST,
            equipment=EquipmentEnum.BARBELL,
            subcategory="Middle Chest"
        )
        db_session.add(exercise)
        db_session.commit()

        # Only update name, leave other fields unchanged
        update_data = ExerciseUpdate(name="Flat Bench Press")
        result = exercise_service.update_exercise(exercise.id, update_data, db_session)

        assert result.name == "Flat Bench Press"
        assert result.category == CategoryEnum.CHEST
        assert result.equipment == EquipmentEnum.BARBELL
        assert result.subcategory == "Middle Chest"


class TestDeleteExercise:
    """Test suite for delete_exercise function."""

    def test_delete_existing_exercise(self, db_session: Session):
        """Test deleting an existing exercise."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()
        exercise_id = exercise.id

        # Delete the exercise
        exercise_service.delete_exercise(exercise_id, db_session)

        # Verify it's deleted
        deleted_exercise = db_session.get(Exercise, exercise_id)
        assert deleted_exercise is None

    def test_delete_nonexistent_exercise(self, db_session: Session):
        """Test deleting a non-existent exercise raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            exercise_service.delete_exercise(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_exercise_returns_none(self, db_session: Session):
        """Test that delete_exercise returns None."""
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST, equipment=EquipmentEnum.BARBELL)
        db_session.add(exercise)
        db_session.commit()

        result = exercise_service.delete_exercise(exercise.id, db_session)
        assert result is None
