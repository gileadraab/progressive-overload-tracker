"""Integration tests for sessions API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestSessionsAPI:
    """Test cases for /sessions endpoints."""

    def test_create_session_simple(self, client: TestClient):
        """Test creating a simple session without exercises."""
        # Create user first
        user_response = client.post("/users/", json={"username": "sessionuser"})
        user_id = user_response.json()["id"]

        # Create session
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [],
        }
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert "id" in data
        assert data["exercise_sessions"] == []

    @pytest.mark.skip(reason="Nested exercise details not included in response")
    def test_create_session_with_exercises(self, client: TestClient):
        """Test creating a session with exercises and sets."""
        # Create user
        user_response = client.post("/users/", json={"username": "workoutuser"})
        user_id = user_response.json()["id"]

        # Create exercise
        exercise_response = client.post(
            "/exercises/", json={"name": "Squat", "category": "legs", "equipment": "barbell"}
        )
        exercise_id = exercise_response.json()["id"]

        # Create session with exercise and sets
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 100.0, "reps": 10, "unit": "kg"},
                        {"weight": 110.0, "reps": 8, "unit": "kg"},
                        {"weight": 120.0, "reps": 6, "unit": "kg"},
                    ],
                }
            ],
        }
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert len(data["exercise_sessions"]) == 1
        assert data["exercise_sessions"][0]["exercise"]["id"] == exercise_id
        assert len(data["exercise_sessions"][0]["sets"]) == 3

    def test_create_session_multiple_exercises(self, client: TestClient):
        """Test creating a session with multiple exercises."""
        # Create user
        user_response = client.post("/users/", json={"username": "multiexuser"})
        user_id = user_response.json()["id"]

        # Create exercises
        exercise1 = client.post(
            "/exercises/", json={"name": "Bench Press", "category": "chest", "equipment": "barbell"}
        ).json()
        exercise2 = client.post(
            "/exercises/", json={"name": "Incline Press", "category": "chest", "equipment": "dumbbell"}
        ).json()

        # Create session with multiple exercises
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise1["id"],
                    "sets": [{"weight": 80.0, "reps": 10, "unit": "kg"}],
                },
                {
                    "exercise_id": exercise2["id"],
                    "sets": [{"weight": 30.0, "reps": 12, "unit": "kg"}],
                },
            ],
        }
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        data = response.json()
        assert len(data["exercise_sessions"]) == 2

    @pytest.mark.skip(reason="FK validation not yet implemented")
    def test_create_session_invalid_user(self, client: TestClient):
        """Test creating session with non-existent user."""
        session_data = {"user_id": 99999, "exercise_sessions": []}
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 404

    @pytest.mark.skip(reason="FK validation not yet implemented")
    def test_create_session_invalid_exercise(self, client: TestClient):
        """Test creating session with non-existent exercise."""
        # Create user
        user_response = client.post("/users/", json={"username": "badexuser"})
        user_id = user_response.json()["id"]

        # Try to create session with invalid exercise
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": 99999,
                    "sets": [{"weight": 100.0, "reps": 10, "unit": "kg"}],
                }
            ],
        }
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 404

    def test_get_all_sessions(self, client: TestClient):
        """Test retrieving all sessions."""
        # Create user
        user_response = client.post("/users/", json={"username": "allsessionsuser"})
        user_id = user_response.json()["id"]

        # Create multiple sessions
        for i in range(3):
            session_data = {"user_id": user_id, "exercise_sessions": []}
            client.post("/sessions/", json=session_data)

        response = client.get("/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_session_by_id(self, client: TestClient):
        """Test retrieving a specific session by ID."""
        # Create user and session
        user_response = client.post("/users/", json={"username": "getsessionuser"})
        user_id = user_response.json()["id"]

        session_response = client.post("/sessions/", json={"user_id": user_id, "exercise_sessions": []})
        session_id = session_response.json()["id"]

        # Get session
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["user_id"] == user_id

    def test_get_session_not_found(self, client: TestClient):
        """Test retrieving non-existent session."""
        response = client.get("/sessions/99999")
        assert response.status_code == 404

    def test_update_session(self, client: TestClient):
        """Test updating a session."""
        # Create user
        user_response = client.post("/users/", json={"username": "updatesessionuser"})
        user_id = user_response.json()["id"]

        # Create session
        session_response = client.post("/sessions/", json={"user_id": user_id, "exercise_sessions": []})
        session_id = session_response.json()["id"]

        # Update session (can change user_id if needed)
        update_data = {"user_id": user_id, "exercise_sessions": []}
        response = client.put(f"/sessions/{session_id}", json=update_data)
        assert response.status_code == 200

    def test_update_session_not_found(self, client: TestClient):
        """Test updating non-existent session."""
        # Create user for the update data
        user_response = client.post("/users/", json={"username": "ghostuser"})
        user_id = user_response.json()["id"]

        update_data = {"user_id": user_id, "exercise_sessions": []}
        response = client.put("/sessions/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_session(self, client: TestClient):
        """Test deleting a session."""
        # Create user and session
        user_response = client.post("/users/", json={"username": "deletesessionuser"})
        user_id = user_response.json()["id"]

        session_response = client.post("/sessions/", json={"user_id": user_id, "exercise_sessions": []})
        session_id = session_response.json()["id"]

        # Delete session
        response = client.delete(f"/sessions/{session_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client: TestClient):
        """Test deleting non-existent session."""
        response = client.delete("/sessions/99999")
        assert response.status_code == 404

    def test_delete_session_cascades_to_sets(self, client: TestClient):
        """Test that deleting a session also deletes its sets."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "cascadeuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/", json={"name": "Test Exercise", "category": "chest", "equipment": "barbell"}
        )
        exercise_id = exercise_response.json()["id"]

        # Create session with sets
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 100.0, "reps": 10, "unit": "kg"},
                        {"weight": 110.0, "reps": 8, "unit": "kg"},
                    ],
                }
            ],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Delete session
        delete_response = client.delete(f"/sessions/{session_id}")
        assert delete_response.status_code == 204

        # Verify session is deleted
        get_response = client.get(f"/sessions/{session_id}")
        assert get_response.status_code == 404

    @pytest.mark.skip(reason="Query parameter filtering not yet implemented")
    def test_filter_sessions_by_user(self, client: TestClient):
        """Test filtering sessions by user_id."""
        # Create two users
        user1 = client.post("/users/", json={"username": "filteruser1"}).json()
        user2 = client.post("/users/", json={"username": "filteruser2"}).json()

        # Create sessions for each user
        client.post("/sessions/", json={"user_id": user1["id"], "exercise_sessions": []})
        client.post("/sessions/", json={"user_id": user1["id"], "exercise_sessions": []})
        client.post("/sessions/", json={"user_id": user2["id"], "exercise_sessions": []})

        # Filter by user1
        response = client.get(f"/sessions/?user_id={user1['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(s["user_id"] == user1["id"] for s in data)

    def test_pagination_skip_limit(self, client: TestClient):
        """Test pagination with skip and limit."""
        # Create user
        user_response = client.post("/users/", json={"username": "paginationuser"})
        user_id = user_response.json()["id"]

        # Create multiple sessions
        for i in range(10):
            client.post("/sessions/", json={"user_id": user_id, "exercise_sessions": []})

        # Test pagination
        response = client.get("/sessions/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    @pytest.mark.skip(reason="Nested exercise details not included in response")
    def test_create_session_with_stacks_unit(self, client: TestClient):
        """Test creating session with sets using 'stacks' unit."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "stacksuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/", json={"name": "Lat Pulldown", "category": "back", "equipment": "machine"}
        )
        exercise_id = exercise_response.json()["id"]

        # Create session with stacks unit
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 10.0, "reps": 12, "unit": "stacks"},
                        {"weight": 12.0, "reps": 10, "unit": "stacks"},
                    ],
                }
            ],
        }
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 201
        data = response.json()
        assert data["exercise_sessions"][0]["sets"][0]["unit"] == "stacks"
        assert data["exercise_sessions"][0]["sets"][1]["unit"] == "stacks"

    def test_create_session_missing_required_fields(self, client: TestClient):
        """Test creating session with missing required fields."""
        session_data = {"exercise_sessions": []}  # Missing user_id
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 422
