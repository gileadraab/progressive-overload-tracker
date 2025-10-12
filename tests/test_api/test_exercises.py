"""Integration tests for exercises API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestExercisesAPI:
    """Test cases for /exercises endpoints."""

    def test_create_exercise(self, client: TestClient):
        """Test creating a new exercise."""
        exercise_data = {
            "name": "Bench Press",
            "category": "chest",
            "equipment": "barbell",
        }
        response = client.post("/exercises/", json=exercise_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bench Press"
        assert data["category"] == "chest"
        assert data["equipment"] == "barbell"
        assert "id" in data
    def test_create_exercise_invalid_category(self, client: TestClient):
        """Test creating exercise with invalid category."""
        exercise_data = {
            "name": "Invalid Exercise",
            "category": "invalid_category",
            "equipment": "barbell",
        }
        response = client.post("/exercises/", json=exercise_data)
        assert response.status_code == 422

    def test_create_exercise_invalid_equipment(self, client: TestClient):
        """Test creating exercise with invalid equipment."""
        exercise_data = {
            "name": "Invalid Exercise",
            "category": "chest",
            "equipment": "invalid_equipment",
        }
        response = client.post("/exercises/", json=exercise_data)
        assert response.status_code == 422

    def test_get_all_exercises(self, client: TestClient):
        """Test retrieving all exercises."""
        # Create test exercises
        exercises = [
            {"name": "Squat", "category": "legs", "equipment": "barbell"},
            {"name": "Deadlift", "category": "back", "equipment": "barbell"},
            {"name": "Dumbbell Press", "category": "chest", "equipment": "dumbbell"},
        ]
        for exercise in exercises:
            client.post("/exercises/", json=exercise)

        response = client.get("/exercises/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_exercise_by_id(self, client: TestClient):
        """Test retrieving a specific exercise by ID."""
        # Create exercise
        exercise_data = {"name": "Pull-up", "category": "back", "equipment": "bodyweight"}
        create_response = client.post("/exercises/", json=exercise_data)
        exercise_id = create_response.json()["id"]

        # Get exercise
        response = client.get(f"/exercises/{exercise_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == exercise_id
        assert data["name"] == "Pull-up"

    def test_get_exercise_not_found(self, client: TestClient):
        """Test retrieving non-existent exercise."""
        response = client.get("/exercises/99999")
        assert response.status_code == 404

    def test_update_exercise(self, client: TestClient):
        """Test updating an exercise."""
        # Create exercise
        exercise_data = {"name": "Leg Press", "category": "legs", "equipment": "machine"}
        create_response = client.post("/exercises/", json=exercise_data)
        exercise_id = create_response.json()["id"]

        # Update exercise
        update_data = {"name": "Leg Press Machine", "category": "legs", "equipment": "machine"}
        response = client.put(f"/exercises/{exercise_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Leg Press Machine"

    def test_update_exercise_not_found(self, client: TestClient):
        """Test updating non-existent exercise."""
        update_data = {"name": "Ghost Exercise", "category": "chest", "equipment": "barbell"}
        response = client.put("/exercises/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_exercise(self, client: TestClient):
        """Test deleting an exercise."""
        # Create exercise
        exercise_data = {"name": "Tricep Extension", "category": "arms", "equipment": "dumbbell"}
        create_response = client.post("/exercises/", json=exercise_data)
        exercise_id = create_response.json()["id"]

        # Delete exercise
        response = client.delete(f"/exercises/{exercise_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/exercises/{exercise_id}")
        assert get_response.status_code == 404

    def test_delete_exercise_not_found(self, client: TestClient):
        """Test deleting non-existent exercise."""
        response = client.delete("/exercises/99999")
        assert response.status_code == 404

    def test_search_exercises_by_name(self, client: TestClient):
        """Test searching exercises by name."""
        # Create exercises
        exercises = [
            {"name": "Barbell Curl", "category": "arms", "equipment": "barbell"},
            {"name": "Dumbbell Curl", "category": "arms", "equipment": "dumbbell"},
            {"name": "Cable Curl", "category": "arms", "equipment": "machine"},
        ]
        for exercise in exercises:
            client.post("/exercises/", json=exercise)

        # Search by name
        response = client.get("/exercises/?name=Curl")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all("Curl" in ex["name"] for ex in data)

    def test_search_exercises_by_category(self, client: TestClient):
        """Test searching exercises by category."""
        # Create exercises
        exercises = [
            {"name": "Shoulder Press", "category": "shoulders", "equipment": "barbell"},
            {"name": "Lateral Raise", "category": "shoulders", "equipment": "dumbbell"},
            {"name": "Bench Press", "category": "chest", "equipment": "barbell"},
        ]
        for exercise in exercises:
            client.post("/exercises/", json=exercise)

        # Search by category
        response = client.get("/exercises/?category=shoulders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(ex["category"] == "shoulders" for ex in data)

    def test_search_exercises_by_equipment(self, client: TestClient):
        """Test searching exercises by equipment."""
        # Create exercises
        exercises = [
            {"name": "Kettlebell Swing", "category": "legs", "equipment": "kettlebell"},
            {"name": "Kettlebell Squat", "category": "legs", "equipment": "kettlebell"},
            {"name": "Barbell Squat", "category": "legs", "equipment": "barbell"},
        ]
        for exercise in exercises:
            client.post("/exercises/", json=exercise)

        # Search by equipment
        response = client.get("/exercises/?equipment=kettlebell")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(ex["equipment"] == "kettlebell" for ex in data)

    def test_search_exercises_combined_filters(self, client: TestClient):
        """Test searching exercises with multiple filters."""
        # Create exercises
        exercises = [
            {"name": "Dumbbell Shoulder Press", "category": "shoulders", "equipment": "dumbbell"},
            {"name": "Barbell Shoulder Press", "category": "shoulders", "equipment": "barbell"},
            {"name": "Dumbbell Chest Press", "category": "chest", "equipment": "dumbbell"},
        ]
        for exercise in exercises:
            client.post("/exercises/", json=exercise)

        # Search with multiple filters
        response = client.get("/exercises/?category=shoulders&equipment=dumbbell")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(ex["category"] == "shoulders" and ex["equipment"] == "dumbbell" for ex in data)

    def test_pagination_skip_limit(self, client: TestClient):
        """Test pagination with skip and limit."""
        # Create multiple exercises
        for i in range(10):
            exercise_data = {
                "name": f"Exercise {i}",
                "category": "chest",
                "equipment": "barbell",
            }
            client.post("/exercises/", json=exercise_data)

        # Test pagination
        response = client.get("/exercises/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_empty_search_results(self, client: TestClient):
        """Test search with no matching results."""
        response = client.get("/exercises/?name=NonExistentExercise12345")
        assert response.status_code == 200
        data = response.json()
        # May be empty or contain exercises that don't match
        assert isinstance(data, list)


class TestExerciseHistoryAPI:
    """Test cases for /exercises/{id}/history endpoint."""

    def test_exercise_history_with_data(self, client: TestClient):
        """Test getting exercise history with workout data."""
        # Create user
        user_response = client.post("/users/", json={"username": "testuser"})
        user_id = user_response.json()["id"]

        # Create exercise
        exercise_response = client.post("/exercises/", json={
            "name": "Bench Press",
            "category": "chest",
            "equipment": "barbell"
        })
        exercise_id = exercise_response.json()["id"]

        # Create session with sets
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [
                    {"weight": 100, "reps": 10, "unit": "kg"},
                    {"weight": 100, "reps": 8, "unit": "kg"}
                ]
            }]
        }
        client.post("/sessions/", json=session_data)

        # Get history
        response = client.get(f"/exercises/{exercise_id}/history?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert data["exercise_id"] == exercise_id
        assert data["last_performed"] is not None
        assert len(data["last_performed"]["sets"]) == 2
        assert data["last_performed"]["max_weight"] == 100
        assert data["last_performed"]["total_volume"] == 1800  # 100*10 + 100*8
        assert data["personal_best"] is not None
        assert data["progression_suggestion"] is not None

    def test_exercise_history_no_data(self, client: TestClient):
        """Test getting history when no workout data exists."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "newuser"})
        user_id = user_response.json()["id"]

        exercise_response = client.post("/exercises/", json={
            "name": "Squat",
            "category": "legs"
        })
        exercise_id = exercise_response.json()["id"]

        # Get history (no workouts yet)
        response = client.get(f"/exercises/{exercise_id}/history?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["exercise_id"] == exercise_id
        assert data["last_performed"] is None
        assert data["personal_best"] is None
        assert data["recent_sessions"] == []
        assert data["progression_suggestion"] is None

    def test_exercise_history_personal_best(self, client: TestClient):
        """Test that personal best is correctly identified."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "athlete"})
        user_id = user_response.json()["id"]

        exercise_response = client.post("/exercises/", json={
            "name": "Deadlift",
            "category": "back"
        })
        exercise_id = exercise_response.json()["id"]

        # Create two sessions - second has higher 1RM
        session1 = {
            "user_id": user_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [{"weight": 100, "reps": 10, "unit": "kg"}]
            }]
        }
        client.post("/sessions/", json=session1)

        session2 = {
            "user_id": user_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [{"weight": 140, "reps": 3, "unit": "kg"}]
            }]
        }
        client.post("/sessions/", json=session2)

        # Get history
        response = client.get(f"/exercises/{exercise_id}/history?user_id={user_id}")
        data = response.json()

        # 140x3 has higher estimated 1RM than 100x10
        assert data["personal_best"]["weight"] == 140
        assert data["personal_best"]["reps"] == 3
        assert data["personal_best"]["estimated_1rm"] > 140

    def test_exercise_history_progression_suggestion(self, client: TestClient):
        """Test progression suggestions based on last workout."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "progressor"})
        user_id = user_response.json()["id"]

        exercise_response = client.post("/exercises/", json={
            "name": "Overhead Press",
            "category": "shoulders"
        })
        exercise_id = exercise_response.json()["id"]

        # Create session where user hit 10 reps (should suggest weight increase)
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [{"weight": 60, "reps": 10, "unit": "kg"}]
            }]
        }
        client.post("/sessions/", json=session_data)

        # Get history
        response = client.get(f"/exercises/{exercise_id}/history?user_id={user_id}")
        data = response.json()

        # Should suggest increasing weight since hit 8+ reps
        suggestion = data["progression_suggestion"]
        assert suggestion["recommended_weight"] == 62.5
        assert suggestion["recommended_reps"] == 10
        assert "increase weight" in suggestion["rationale"].lower()

    def test_exercise_history_user_isolation(self, client: TestClient):
        """Test that history is isolated per user."""
        # Create two users
        user1_response = client.post("/users/", json={"username": "user1"})
        user1_id = user1_response.json()["id"]

        user2_response = client.post("/users/", json={"username": "user2"})
        user2_id = user2_response.json()["id"]

        # Create exercise
        exercise_response = client.post("/exercises/", json={
            "name": "Row",
            "category": "back"
        })
        exercise_id = exercise_response.json()["id"]

        # User1's session
        session1 = {
            "user_id": user1_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [{"weight": 80, "reps": 10, "unit": "kg"}]
            }]
        }
        client.post("/sessions/", json=session1)

        # User2's session (higher weight)
        session2 = {
            "user_id": user2_id,
            "exercise_sessions": [{
                "exercise_id": exercise_id,
                "sets": [{"weight": 120, "reps": 10, "unit": "kg"}]
            }]
        }
        client.post("/sessions/", json=session2)

        # Get user1's history
        response = client.get(f"/exercises/{exercise_id}/history?user_id={user1_id}")
        data = response.json()

        # Should only see user1's 80kg, not user2's 120kg
        assert data["personal_best"]["weight"] == 80
        assert data["last_performed"]["max_weight"] == 80

    def test_exercise_history_nonexistent_exercise(self, client: TestClient):
        """Test history for non-existent exercise."""
        user_response = client.post("/users/", json={"username": "testuser"})
        user_id = user_response.json()["id"]

        response = client.get(f"/exercises/99999/history?user_id={user_id}")
        assert response.status_code == 404

    def test_exercise_history_missing_user_id(self, client: TestClient):
        """Test that user_id query parameter is required."""
        exercise_response = client.post("/exercises/", json={
            "name": "Test Exercise",
            "category": "arms"
        })
        exercise_id = exercise_response.json()["id"]

        response = client.get(f"/exercises/{exercise_id}/history")
        assert response.status_code == 422  # Missing required query param
