"""Integration tests for users API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestUsersAPI:
    """Test cases for /users endpoints."""

    def test_create_user(self, client: TestClient):
        """Test creating a new user."""
        user_data = {
            "username": "testuser123",
            "name": "Test User",
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser123"
        assert data["name"] == "Test User"
        assert "id" in data

    def test_create_user_without_display_name(self, client: TestClient):
        """Test creating user without display name (optional field)."""
        user_data = {"username": "simpleuser"}
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "simpleuser"
        assert data["name"] is None

    def test_create_user_duplicate_username(self, client: TestClient):
        """Test creating user with duplicate username."""
        user_data = {"username": "duplicate_user"}

        # Create first user
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == 201

        # Try to create second user with same username
        response2 = client.post("/users/", json=user_data)
        assert response2.status_code == 400
        detail = response2.json()["detail"].lower()
        assert "already exists" in detail or "already taken" in detail

    def test_create_user_missing_username(self, client: TestClient):
        """Test creating user without username."""
        user_data = {"name": "No Username"}
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422

    def test_get_all_users(self, client: TestClient):
        """Test retrieving all users."""
        # Create test users
        users = [
            {"username": "user1", "name": "User One"},
            {"username": "user2", "name": "User Two"},
            {"username": "user3", "name": "User Three"},
        ]
        for user in users:
            client.post("/users/", json=user)

        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_user_by_id(self, client: TestClient):
        """Test retrieving a specific user by ID."""
        # Create user
        user_data = {"username": "getuser", "name": "Get User"}
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Get user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "getuser"
        assert data["name"] == "Get User"

    def test_get_user_not_found(self, client: TestClient):
        """Test retrieving non-existent user."""
        response = client.get("/users/99999")
        assert response.status_code == 404

    def test_update_user(self, client: TestClient):
        """Test updating a user."""
        # Create user
        user_data = {"username": "olduser", "name": "Old Name"}
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Update user
        update_data = {"username": "olduser", "name": "New Name"}
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["username"] == "olduser"

    def test_update_user_change_username(self, client: TestClient):
        """Test changing username during update."""
        # Create user
        user_data = {"username": "originalname"}
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Update username
        update_data = {"username": "newname", "name": "Updated User"}
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newname"

    def test_update_user_not_found(self, client: TestClient):
        """Test updating non-existent user."""
        update_data = {"username": "ghost", "name": "Ghost User"}
        response = client.put("/users/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_user(self, client: TestClient):
        """Test deleting a user."""
        # Create user
        user_data = {"username": "deleteuser"}
        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Delete user
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Test deleting non-existent user."""
        response = client.delete("/users/99999")
        assert response.status_code == 404

    def test_delete_user_with_sessions_cascade(self, client: TestClient):
        """Test that deleting a user cascades to delete their sessions."""
        # Create user
        user_data = {"username": "userwithhsessions"}
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]

        # Create session for user
        session_data = {
            "user_id": user_id,
            "exercises": [],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Delete user
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify user is deleted
        user_get = client.get(f"/users/{user_id}")
        assert user_get.status_code == 404

        # Verify session is also deleted (cascade)
        session_get = client.get(f"/sessions/{session_id}")
        assert session_get.status_code == 404

    def test_pagination_skip_limit(self, client: TestClient):
        """Test pagination with skip and limit."""
        # Create multiple users
        for i in range(10):
            user_data = {"username": f"paginationuser{i}"}
            client.post("/users/", json=user_data)

        # Test pagination
        response = client.get("/users/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_create_user_empty_username(self, client: TestClient):
        """Test creating user with empty username."""
        user_data = {"username": ""}
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422

    def test_user_with_long_username(self, client: TestClient):
        """Test creating user with very long username."""
        user_data = {"username": "a" * 100}
        response = client.post("/users/", json=user_data)
        # Should succeed unless there's a length constraint
        assert response.status_code in [201, 422]

    @pytest.mark.skip(reason="UserWithSessions response not yet implemented")
    def test_get_user_with_sessions(self, client: TestClient):
        """Test retrieving user includes their sessions."""
        # Create user
        user_data = {"username": "userwithsessions2"}
        user_response = client.post("/users/", json=user_data)
        user_id = user_response.json()["id"]

        # Create sessions for user
        for i in range(3):
            session_data = {"user_id": user_id, "exercises": []}
            client.post("/sessions/", json=session_data)

        # Get user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 3
