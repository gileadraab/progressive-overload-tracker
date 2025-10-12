import pytest
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise import Exercise, CategoryEnum, EquipmentEnum
from src.models.user import User
from src.models.session import Session as WorkoutSession
from src.models.exercise_session import ExerciseSession
from src.models.set import Set
from src.models.enums import UnitEnum
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


class TestCalculateOneRepMax:
    """Test suite for calculate_one_rep_max function."""

    def test_one_rep_max_formula(self):
        """Test Brzycki formula for various weights and reps."""
        # 100kg x 10 reps should give ~133.33kg 1RM
        result = exercise_service.calculate_one_rep_max(100, 10)
        assert abs(result - 133.33) < 0.01

        # 80kg x 8 reps should give ~99.31kg 1RM
        result = exercise_service.calculate_one_rep_max(80, 8)
        assert abs(result - 99.31) < 0.01

    def test_one_rep_is_weight(self):
        """Test that 1 rep returns the weight itself."""
        result = exercise_service.calculate_one_rep_max(100, 1)
        assert result == 100

    def test_high_reps_returns_weight(self):
        """Test that formula doesn't break for high reps (37+)."""
        result = exercise_service.calculate_one_rep_max(50, 40)
        assert result == 50  # Should just return weight


class TestCalculateProgression:
    """Test suite for calculate_progression function."""

    def test_progression_increase_weight_when_hit_target_reps(self):
        """Test progression increases weight when user hits 8+ reps."""
        recent_sets = [
            {"weight": 100, "reps": 10, "unit": "kg"},
            {"weight": 100, "reps": 8, "unit": "kg"}
        ]

        result = exercise_service.calculate_progression(recent_sets)
        assert result["recommended_weight"] == 102.5
        assert result["recommended_reps"] == 10
        assert "increase weight" in result["rationale"].lower()

    def test_progression_increase_reps_when_below_target(self):
        """Test progression increases reps when below 8 reps."""
        recent_sets = [
            {"weight": 100, "reps": 6, "unit": "kg"},
            {"weight": 100, "reps": 5, "unit": "kg"}
        ]

        result = exercise_service.calculate_progression(recent_sets)
        assert result["recommended_weight"] == 100
        assert result["recommended_reps"] == 7  # 6 + 1
        assert "more reps" in result["rationale"].lower()

    def test_progression_empty_sets(self):
        """Test progression returns None for empty sets."""
        result = exercise_service.calculate_progression([])
        assert result is None

    def test_progression_selects_best_set_by_volume(self):
        """Test progression uses best set (highest volume)."""
        recent_sets = [
            {"weight": 90, "reps": 10, "unit": "kg"},  # Volume: 900
            {"weight": 100, "reps": 6, "unit": "kg"},  # Volume: 600
        ]

        result = exercise_service.calculate_progression(recent_sets)
        # Should use 90x10 (higher volume) as reference
        assert result["recommended_weight"] == 92.5
        assert result["recommended_reps"] == 10

    def test_progression_with_stacks_unit(self):
        """Test progression uses 1 stack increment for stacks unit."""
        recent_sets = [
            {"weight": 10, "reps": 10, "unit": "stacks"}
        ]

        result = exercise_service.calculate_progression(recent_sets)
        # Should increment by 1 stack, not 2.5
        assert result["recommended_weight"] == 11
        assert result["recommended_reps"] == 10
        assert "1 stack" in result["rationale"]


class TestGetExerciseHistory:
    """Test suite for get_exercise_history function."""

    def test_exercise_history_basic(self, db_session: Session):
        """Test getting basic exercise history."""
        # Create user and exercise
        user = User(username="testuser")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add(user)
        db_session.add(exercise)
        db_session.commit()

        # Create session with sets
        session = WorkoutSession(user_id=user.id, date=datetime(2025, 10, 1))
        db_session.add(session)
        db_session.commit()

        ex_session = ExerciseSession(exercise_id=exercise.id, session_id=session.id)
        db_session.add(ex_session)
        db_session.commit()

        sets = [
            Set(weight=100, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session.id),
            Set(weight=100, reps=8, unit=UnitEnum.kg, exercise_session_id=ex_session.id)
        ]
        for s in sets:
            db_session.add(s)
        db_session.commit()

        # Get history
        result = exercise_service.get_exercise_history(exercise.id, user.id, db_session)

        assert result["exercise_id"] == exercise.id
        assert result["last_performed"] is not None
        assert result["last_performed"]["session_id"] == session.id
        assert len(result["last_performed"]["sets"]) == 2
        assert result["last_performed"]["max_weight"] == 100
        assert result["last_performed"]["total_volume"] == 1800  # 100*10 + 100*8

    def test_exercise_history_personal_best(self, db_session: Session):
        """Test personal best calculation across multiple sessions."""
        user = User(username="testuser")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add(user)
        db_session.add(exercise)
        db_session.commit()

        # Session 1: 100kg x 10
        session1 = WorkoutSession(user_id=user.id, date=datetime(2025, 9, 1))
        db_session.add(session1)
        db_session.commit()
        ex_session1 = ExerciseSession(exercise_id=exercise.id, session_id=session1.id)
        db_session.add(ex_session1)
        db_session.commit()
        db_session.add(Set(weight=100, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session1.id))

        # Session 2: 120kg x 5 (higher 1RM)
        session2 = WorkoutSession(user_id=user.id, date=datetime(2025, 10, 1))
        db_session.add(session2)
        db_session.commit()
        ex_session2 = ExerciseSession(exercise_id=exercise.id, session_id=session2.id)
        db_session.add(ex_session2)
        db_session.commit()
        db_session.add(Set(weight=120, reps=5, unit=UnitEnum.kg, exercise_session_id=ex_session2.id))
        db_session.commit()

        result = exercise_service.get_exercise_history(exercise.id, user.id, db_session)

        # 120x5 should be the PR (higher estimated 1RM than 100x10)
        assert result["personal_best"]["weight"] == 120
        assert result["personal_best"]["reps"] == 5
        assert result["personal_best"]["estimated_1rm"] > 130

    def test_exercise_history_recent_sessions(self, db_session: Session):
        """Test recent sessions summary (last 5)."""
        user = User(username="testuser")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add(user)
        db_session.add(exercise)
        db_session.commit()

        # Create 7 sessions (should only return last 5)
        for i in range(7):
            session = WorkoutSession(user_id=user.id, date=datetime(2025, 9, i + 1))
            db_session.add(session)
            db_session.commit()
            ex_session = ExerciseSession(exercise_id=exercise.id, session_id=session.id)
            db_session.add(ex_session)
            db_session.commit()
            db_session.add(Set(weight=100 + i, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session.id))
        db_session.commit()

        result = exercise_service.get_exercise_history(exercise.id, user.id, db_session)

        assert len(result["recent_sessions"]) == 5
        # Most recent should be first
        assert result["recent_sessions"][0]["best_set"]["weight"] == 106

    def test_exercise_history_progression_suggestion(self, db_session: Session):
        """Test progression suggestion in history."""
        user = User(username="testuser")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add(user)
        db_session.add(exercise)
        db_session.commit()

        session = WorkoutSession(user_id=user.id, date=datetime(2025, 10, 1))
        db_session.add(session)
        db_session.commit()
        ex_session = ExerciseSession(exercise_id=exercise.id, session_id=session.id)
        db_session.add(ex_session)
        db_session.commit()
        db_session.add(Set(weight=100, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session.id))
        db_session.commit()

        result = exercise_service.get_exercise_history(exercise.id, user.id, db_session)

        assert result["progression_suggestion"] is not None
        assert result["progression_suggestion"]["recommended_weight"] == 102.5

    def test_exercise_history_no_data(self, db_session: Session):
        """Test history when no workout data exists."""
        user = User(username="testuser")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add(user)
        db_session.add(exercise)
        db_session.commit()

        result = exercise_service.get_exercise_history(exercise.id, user.id, db_session)

        assert result["exercise_id"] == exercise.id
        assert result["last_performed"] is None
        assert result["personal_best"] is None
        assert result["recent_sessions"] == []
        assert result["progression_suggestion"] is None

    def test_exercise_history_nonexistent_exercise(self, db_session: Session):
        """Test history for non-existent exercise raises HTTPException."""
        user = User(username="testuser")
        db_session.add(user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            exercise_service.get_exercise_history(999, user.id, db_session)
        assert exc_info.value.status_code == 404

    def test_exercise_history_filters_by_user(self, db_session: Session):
        """Test that history only includes data for specified user."""
        user1 = User(username="user1")
        user2 = User(username="user2")
        exercise = Exercise(name="Bench Press", category=CategoryEnum.CHEST)
        db_session.add_all([user1, user2, exercise])
        db_session.commit()

        # User1's session
        session1 = WorkoutSession(user_id=user1.id, date=datetime(2025, 10, 1))
        db_session.add(session1)
        db_session.commit()
        ex_session1 = ExerciseSession(exercise_id=exercise.id, session_id=session1.id)
        db_session.add(ex_session1)
        db_session.commit()
        db_session.add(Set(weight=100, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session1.id))

        # User2's session
        session2 = WorkoutSession(user_id=user2.id, date=datetime(2025, 10, 2))
        db_session.add(session2)
        db_session.commit()
        ex_session2 = ExerciseSession(exercise_id=exercise.id, session_id=session2.id)
        db_session.add(ex_session2)
        db_session.commit()
        db_session.add(Set(weight=200, reps=10, unit=UnitEnum.kg, exercise_session_id=ex_session2.id))
        db_session.commit()

        # Get user1's history
        result = exercise_service.get_exercise_history(exercise.id, user1.id, db_session)

        # Should only see user1's 100kg, not user2's 200kg
        assert result["last_performed"]["max_weight"] == 100
        assert result["personal_best"]["weight"] == 100
