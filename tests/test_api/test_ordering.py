"""Integration tests for ordering functionality."""
import pytest
from fastapi.testclient import TestClient

from src.models.enums import CategoryEnum, EquipmentEnum
from src.models.exercise import Exercise


@pytest.fixture
def bench_press(db_session) -> Exercise:
    """Create a bench press exercise for testing."""
    exercise = Exercise(
        name="Bench Press Barbell",
        category=CategoryEnum.CHEST,
        equipment=EquipmentEnum.BARBELL,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


class TestOrderingFunctionality:
    """Test exercise and set ordering features."""

    def test_create_session_assigns_default_order(
        self, client: TestClient, sample_user, sample_exercise
    ):
        """Test that creating a session assigns default order values."""
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [
                        {"weight": 100, "reps": 10, "unit": "kg"},
                        {"weight": 110, "reps": 8, "unit": "kg"},
                        {"weight": 120, "reps": 6, "unit": "kg"},
                    ],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201

        data = response.json()
        # Exercise session should have order 1
        assert data["exercise_sessions"][0]["order"] == 1

        # Sets should have order 1, 2, 3
        sets = data["exercise_sessions"][0]["sets"]
        assert len(sets) == 3
        assert sets[0]["order"] == 1
        assert sets[1]["order"] == 2
        assert sets[2]["order"] == 3

    def test_create_session_with_explicit_order(
        self, client: TestClient, sample_user, sample_exercise
    ):
        """Test creating a session with explicitly specified order values."""
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "order": 5,
                    "sets": [
                        {"weight": 100, "reps": 10, "unit": "kg", "order": 10},
                        {"weight": 110, "reps": 8, "unit": "kg", "order": 20},
                    ],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201

        data = response.json()
        # Should use the explicitly provided order values
        assert data["exercise_sessions"][0]["order"] == 5
        assert data["exercise_sessions"][0]["sets"][0]["order"] == 10
        assert data["exercise_sessions"][0]["sets"][1]["order"] == 20

    def test_reorder_exercises_in_session(
        self, client: TestClient, sample_user, sample_exercise, bench_press
    ):
        """Test reordering exercises within a session."""
        # Create session with 2 exercises
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [{"weight": 100, "reps": 10, "unit": "kg"}],
                },
                {
                    "exercise_id": bench_press.id,
                    "sets": [{"weight": 80, "reps": 12, "unit": "kg"}],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        session = response.json()

        # Get exercise_session IDs
        es1_id = session["exercise_sessions"][0]["id"]
        es2_id = session["exercise_sessions"][1]["id"]

        # Reorder: swap the two exercises
        reorder_data = {
            "exercise_sessions": [
                {"id": es2_id, "order": 1},  # bench_press first now
                {"id": es1_id, "order": 2},  # exercise second now
            ]
        }

        response = client.patch(f"/sessions/{session['id']}/reorder", json=reorder_data)
        assert response.status_code == 200

        data = response.json()
        # Verify new order
        assert data["exercise_sessions"][0]["id"] == es2_id
        assert data["exercise_sessions"][0]["order"] == 1
        assert data["exercise_sessions"][1]["id"] == es1_id
        assert data["exercise_sessions"][1]["order"] == 2

    def test_reorder_sets_within_exercise(
        self, client: TestClient, sample_user, sample_exercise
    ):
        """Test reordering sets within an exercise session."""
        # Create session with 3 sets
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [
                        {"weight": 100, "reps": 10, "unit": "kg"},
                        {"weight": 110, "reps": 8, "unit": "kg"},
                        {"weight": 120, "reps": 6, "unit": "kg"},
                    ],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        session = response.json()

        es_id = session["exercise_sessions"][0]["id"]
        sets = session["exercise_sessions"][0]["sets"]
        set1_id, set2_id, set3_id = sets[0]["id"], sets[1]["id"], sets[2]["id"]

        # Reorder: move heaviest set (120kg) to first position
        reorder_data = {
            "exercise_sessions": [
                {
                    "id": es_id,
                    "sets": [
                        {"id": set3_id, "order": 1},  # 120kg first
                        {"id": set1_id, "order": 2},  # 100kg second
                        {"id": set2_id, "order": 3},  # 110kg third
                    ],
                }
            ]
        }

        response = client.patch(f"/sessions/{session['id']}/reorder", json=reorder_data)
        assert response.status_code == 200

        data = response.json()
        reordered_sets = data["exercise_sessions"][0]["sets"]

        # Verify new order
        assert reordered_sets[0]["id"] == set3_id
        assert reordered_sets[0]["weight"] == 120
        assert reordered_sets[0]["order"] == 1

        assert reordered_sets[1]["id"] == set1_id
        assert reordered_sets[1]["weight"] == 100
        assert reordered_sets[1]["order"] == 2

        assert reordered_sets[2]["id"] == set2_id
        assert reordered_sets[2]["weight"] == 110
        assert reordered_sets[2]["order"] == 3

    def test_reorder_both_exercises_and_sets(
        self, client: TestClient, sample_user, sample_exercise, bench_press
    ):
        """Test reordering exercises and sets simultaneously."""
        # Create session with 2 exercises, each with 2 sets
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [
                        {"weight": 100, "reps": 10, "unit": "kg"},
                        {"weight": 110, "reps": 8, "unit": "kg"},
                    ],
                },
                {
                    "exercise_id": bench_press.id,
                    "sets": [
                        {"weight": 80, "reps": 12, "unit": "kg"},
                        {"weight": 90, "reps": 10, "unit": "kg"},
                    ],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        session = response.json()

        es1_id = session["exercise_sessions"][0]["id"]
        es2_id = session["exercise_sessions"][1]["id"]
        es1_sets = session["exercise_sessions"][0]["sets"]
        es2_sets = session["exercise_sessions"][1]["sets"]

        # Reorder both exercises and their sets
        reorder_data = {
            "exercise_sessions": [
                {
                    "id": es2_id,
                    "order": 1,  # bench_press first
                    "sets": [
                        {"id": es2_sets[1]["id"], "order": 1},  # 90kg first
                        {"id": es2_sets[0]["id"], "order": 2},  # 80kg second
                    ],
                },
                {
                    "id": es1_id,
                    "order": 2,  # exercise second
                    "sets": [
                        {"id": es1_sets[1]["id"], "order": 1},  # 110kg first
                        {"id": es1_sets[0]["id"], "order": 2},  # 100kg second
                    ],
                },
            ]
        }

        response = client.patch(f"/sessions/{session['id']}/reorder", json=reorder_data)
        assert response.status_code == 200

        data = response.json()
        # Verify exercise order
        assert data["exercise_sessions"][0]["id"] == es2_id
        assert data["exercise_sessions"][1]["id"] == es1_id

        # Verify set order for first exercise (bench_press)
        assert data["exercise_sessions"][0]["sets"][0]["weight"] == 90
        assert data["exercise_sessions"][0]["sets"][1]["weight"] == 80

        # Verify set order for second exercise
        assert data["exercise_sessions"][1]["sets"][0]["weight"] == 110
        assert data["exercise_sessions"][1]["sets"][1]["weight"] == 100

    def test_reorder_invalid_session(self, client: TestClient):
        """Test reordering with non-existent session."""
        reorder_data = {"exercise_sessions": [{"id": 999, "order": 1}]}

        response = client.patch("/sessions/999/reorder", json=reorder_data)
        assert response.status_code == 404

    def test_reorder_invalid_exercise_session(
        self, client: TestClient, sample_user, sample_exercise
    ):
        """Test reordering with non-existent exercise_session."""
        # Create session
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [{"weight": 100, "reps": 10, "unit": "kg"}],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        session = response.json()

        # Try to reorder with non-existent exercise_session ID
        reorder_data = {"exercise_sessions": [{"id": 999999, "order": 1}]}

        response = client.patch(f"/sessions/{session['id']}/reorder", json=reorder_data)
        assert response.status_code == 404
        assert "ExerciseSession" in response.json()["detail"]

    def test_reorder_exercise_session_from_different_session(
        self, client: TestClient, sample_user, sample_exercise
    ):
        """Test that you can't reorder exercise_sessions that belong to a different session."""
        # Create two sessions
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": sample_exercise.id,
                    "sets": [{"weight": 100, "reps": 10, "unit": "kg"}],
                },
            ],
        }

        response1 = client.post("/sessions/", json=session_data)
        session1 = response1.json()

        response2 = client.post("/sessions/", json=session_data)
        session2 = response2.json()

        es1_id = session1["exercise_sessions"][0]["id"]

        # Try to reorder session2 using exercise_session from session1
        reorder_data = {"exercise_sessions": [{"id": es1_id, "order": 1}]}

        response = client.patch(
            f"/sessions/{session2['id']}/reorder", json=reorder_data
        )
        assert response.status_code == 400
        assert "does not belong to session" in response.json()["detail"]

    def test_copy_session_preserves_order(
        self, client: TestClient, sample_user, sample_exercise, bench_press
    ):
        """Test that copying a session preserves the order values."""
        # Create session with explicit order
        session_data = {
            "user_id": sample_user.id,
            "exercise_sessions": [
                {
                    "exercise_id": bench_press.id,
                    "order": 2,
                    "sets": [
                        {"weight": 80, "reps": 12, "unit": "kg", "order": 2},
                        {"weight": 90, "reps": 10, "unit": "kg", "order": 1},
                    ],
                },
                {
                    "exercise_id": sample_exercise.id,
                    "order": 1,
                    "sets": [{"weight": 100, "reps": 10, "unit": "kg", "order": 1}],
                },
            ],
        }

        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        session = response.json()

        # Copy the session
        response = client.get(
            f"/sessions/from-session/{session['id']}",
            params={"user_id": sample_user.id},
        )
        assert response.status_code == 200
        template = response.json()

        # Verify order is preserved (returned sorted by order field)
        # First exercise session should have order 1 (was sample_exercise)
        assert template["exercise_sessions"][0]["order"] == 1
        assert template["exercise_sessions"][0]["exercise_id"] == sample_exercise.id
        # Second exercise session should have order 2 (was bench_press)
        assert template["exercise_sessions"][1]["order"] == 2
        assert template["exercise_sessions"][1]["exercise_id"] == bench_press.id
        # Verify sets order is preserved (bench_press had reverse order sets)
        assert template["exercise_sessions"][1]["sets"][0]["order"] == 1
        assert template["exercise_sessions"][1]["sets"][1]["order"] == 2

    def test_template_with_order(
        self, client: TestClient, sample_user, sample_exercise, bench_press
    ):
        """Test that templates support ordering."""
        # Create template with exercise order
        template_data = {
            "name": "Upper Body",
            "user_id": sample_user.id,
            "exercise_sessions": [
                {"exercise_id": bench_press.id, "order": 2},
                {"exercise_id": sample_exercise.id, "order": 1},
            ],
        }

        response = client.post("/templates/", json=template_data)
        assert response.status_code == 201
        template = response.json()

        # Verify order is stored
        assert template["exercise_sessions"][0]["order"] == 1  # Sorted by order
        assert template["exercise_sessions"][1]["order"] == 2
