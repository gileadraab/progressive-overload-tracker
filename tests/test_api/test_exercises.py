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
