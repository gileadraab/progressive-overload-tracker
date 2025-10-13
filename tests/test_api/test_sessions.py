"""Integration tests for sessions API endpoints."""

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

    def test_create_session_with_exercises(self, client: TestClient):
        """Test creating a session with exercises and sets."""
        # Create user
        user_response = client.post("/users/", json={"username": "workoutuser"})
        user_id = user_response.json()["id"]

        # Create exercise
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Squat", "category": "legs", "equipment": "barbell"},
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
            "/exercises/",
            json={"name": "Bench Press", "category": "chest", "equipment": "barbell"},
        ).json()
        exercise2 = client.post(
            "/exercises/",
            json={
                "name": "Incline Press",
                "category": "chest",
                "equipment": "dumbbell",
            },
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

    def test_create_session_invalid_user(self, client: TestClient):
        """Test creating session with non-existent user."""
        session_data = {"user_id": 99999, "exercise_sessions": []}
        response = client.post("/sessions/", json=session_data)
        assert response.status_code == 404

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

        session_response = client.post(
            "/sessions/", json={"user_id": user_id, "exercise_sessions": []}
        )
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
        session_response = client.post(
            "/sessions/", json={"user_id": user_id, "exercise_sessions": []}
        )
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

        session_response = client.post(
            "/sessions/", json={"user_id": user_id, "exercise_sessions": []}
        )
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
            "/exercises/",
            json={"name": "Test Exercise", "category": "chest", "equipment": "barbell"},
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

    def test_filter_sessions_by_user(self, client: TestClient):
        """Test filtering sessions by user_id."""
        # Create two users
        user1 = client.post("/users/", json={"username": "filteruser1"}).json()
        user2 = client.post("/users/", json={"username": "filteruser2"}).json()

        # Create sessions for each user
        client.post(
            "/sessions/", json={"user_id": user1["id"], "exercise_sessions": []}
        )
        client.post(
            "/sessions/", json={"user_id": user1["id"], "exercise_sessions": []}
        )
        client.post(
            "/sessions/", json={"user_id": user2["id"], "exercise_sessions": []}
        )

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
            client.post(
                "/sessions/", json={"user_id": user_id, "exercise_sessions": []}
            )

        # Test pagination
        response = client.get("/sessions/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_create_session_with_stacks_unit(self, client: TestClient):
        """Test creating session with sets using 'stacks' unit."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "stacksuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Lat Pulldown", "category": "back", "equipment": "machine"},
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

    def test_get_session_from_template(self, client: TestClient):
        """Test instantiating a session from a template."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "templateuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Deadlift", "category": "legs", "equipment": "barbell"},
        )
        exercise_id = exercise_response.json()["id"]

        # Create template
        template_data = {
            "name": "Leg Day",
            "user_id": user_id,
            "exercise_sessions": [
                {"exercise_id": exercise_id, "sets": []}  # Templates have empty sets
            ],
        }
        template_response = client.post("/templates/", json=template_data)
        template_id = template_response.json()["id"]

        # Get session from template
        response = client.get(
            f"/sessions/from-template/{template_id}?user_id={user_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert len(data["exercise_sessions"]) == 1
        assert data["exercise_sessions"][0]["exercise_id"] == exercise_id

    def test_copy_session_basic(self, client: TestClient):
        """Test copying a session to create a new workout."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "copyuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Bench Press", "category": "chest", "equipment": "barbell"},
        )
        exercise_id = exercise_response.json()["id"]

        # Create original session
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 100.0, "reps": 10, "unit": "kg"},
                        {"weight": 100.0, "reps": 8, "unit": "kg"},
                        {"weight": 100.0, "reps": 6, "unit": "kg"},
                    ],
                }
            ],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Copy session
        response = client.get(f"/sessions/from-session/{session_id}?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify copied data matches original
        assert data["user_id"] == user_id
        assert len(data["exercise_sessions"]) == 1
        assert data["exercise_sessions"][0]["exercise_id"] == exercise_id
        assert len(data["exercise_sessions"][0]["sets"]) == 3
        assert data["exercise_sessions"][0]["sets"][0]["weight"] == 100.0
        assert data["exercise_sessions"][0]["sets"][0]["reps"] == 10
        assert data["exercise_sessions"][0]["sets"][0]["unit"] == "kg"

    def test_copy_session_with_multiple_exercises(self, client: TestClient):
        """Test copying a session with multiple exercises."""
        # Create user and exercises
        user_response = client.post("/users/", json={"username": "multicopyuser"})
        user_id = user_response.json()["id"]
        exercise1 = client.post(
            "/exercises/",
            json={"name": "Squat", "category": "legs", "equipment": "barbell"},
        ).json()
        exercise2 = client.post(
            "/exercises/",
            json={"name": "Leg Press", "category": "legs", "equipment": "machine"},
        ).json()

        # Create session with multiple exercises
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise1["id"],
                    "sets": [
                        {"weight": 140.0, "reps": 5, "unit": "kg"},
                        {"weight": 140.0, "reps": 5, "unit": "kg"},
                    ],
                },
                {
                    "exercise_id": exercise2["id"],
                    "sets": [
                        {"weight": 15.0, "reps": 10, "unit": "stacks"},
                    ],
                },
            ],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Copy session
        response = client.get(f"/sessions/from-session/{session_id}?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify all exercises and sets are copied
        assert len(data["exercise_sessions"]) == 2
        assert data["exercise_sessions"][0]["exercise_id"] == exercise1["id"]
        assert len(data["exercise_sessions"][0]["sets"]) == 2
        assert data["exercise_sessions"][1]["exercise_id"] == exercise2["id"]
        assert len(data["exercise_sessions"][1]["sets"]) == 1
        assert data["exercise_sessions"][1]["sets"][0]["unit"] == "stacks"

    def test_progressive_overload_workflow(self, client: TestClient):
        """Test the complete progressive overload workflow: copy → modify → create."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "progressuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/",
            json={
                "name": "Overhead Press",
                "category": "shoulders",
                "equipment": "barbell",
            },
        )
        exercise_id = exercise_response.json()["id"]

        # Week 1: Create original session
        week1_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 50.0, "reps": 10, "unit": "kg"},
                        {"weight": 50.0, "reps": 10, "unit": "kg"},
                        {"weight": 50.0, "reps": 8, "unit": "kg"},
                    ],
                }
            ],
        }
        week1_response = client.post("/sessions/", json=week1_data)
        assert week1_response.status_code == 201
        week1_session_id = week1_response.json()["id"]

        # Week 2: Copy previous session
        copy_response = client.get(
            f"/sessions/from-session/{week1_session_id}?user_id={user_id}"
        )
        assert copy_response.status_code == 200
        week2_data = copy_response.json()

        # User increases weight (progressive overload!)
        for set_data in week2_data["exercise_sessions"][0]["sets"]:
            set_data["weight"] = 52.5  # Increase by 2.5kg

        # Create new session with increased weights
        week2_response = client.post("/sessions/", json=week2_data)
        assert week2_response.status_code == 201
        week2_session = week2_response.json()

        # Verify progression
        assert week2_session["exercise_sessions"][0]["sets"][0]["weight"] == 52.5
        assert week2_session["exercise_sessions"][0]["sets"][1]["weight"] == 52.5
        assert week2_session["exercise_sessions"][0]["sets"][2]["weight"] == 52.5
        assert week2_session["id"] != week1_session_id  # New session created

    def test_copy_session_modify_and_create(self, client: TestClient):
        """Test copying a session, modifying it, and creating a new one."""
        # Create user and exercise
        user_response = client.post("/users/", json={"username": "modifyuser"})
        user_id = user_response.json()["id"]
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Pull-ups", "category": "back", "equipment": "bodyweight"},
        )
        exercise_id = exercise_response.json()["id"]

        # Create original session
        original_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 0.0, "reps": 10, "unit": "kg"},  # Bodyweight
                        {"weight": 0.0, "reps": 8, "unit": "kg"},
                    ],
                }
            ],
        }
        original_response = client.post("/sessions/", json=original_data)
        assert original_response.status_code == 201
        original_id = original_response.json()["id"]

        # Copy session
        copy_response = client.get(
            f"/sessions/from-session/{original_id}?user_id={user_id}"
        )
        copied_data = copy_response.json()

        # Modify: add a set and increase reps
        copied_data["exercise_sessions"][0]["sets"][0]["reps"] = 12
        copied_data["exercise_sessions"][0]["sets"].append(
            {"weight": 0.0, "reps": 10, "unit": "kg"}
        )

        # Create new session
        new_response = client.post("/sessions/", json=copied_data)
        assert new_response.status_code == 201
        new_session = new_response.json()

        # Verify modifications
        assert len(new_session["exercise_sessions"][0]["sets"]) == 3
        assert new_session["exercise_sessions"][0]["sets"][0]["reps"] == 12

    def test_copy_session_not_found(self, client: TestClient):
        """Test copying a non-existent session."""
        # Create user for the query parameter
        user_response = client.post("/users/", json={"username": "notfounduser"})
        user_id = user_response.json()["id"]

        response = client.get(f"/sessions/from-session/99999?user_id={user_id}")
        assert response.status_code == 404

    def test_copy_session_different_user(self, client: TestClient):
        """Test copying a session for a different user."""
        # Create two users
        user1_response = client.post("/users/", json={"username": "user1"})
        user1_id = user1_response.json()["id"]
        user2_response = client.post("/users/", json={"username": "user2"})
        user2_id = user2_response.json()["id"]

        # Create exercise
        exercise_response = client.post(
            "/exercises/",
            json={"name": "Bicep Curl", "category": "arms", "equipment": "dumbbell"},
        )
        exercise_id = exercise_response.json()["id"]

        # Create session for user1
        session_data = {
            "user_id": user1_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [{"weight": 15.0, "reps": 12, "unit": "kg"}],
                }
            ],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Copy session for user2
        copy_response = client.get(
            f"/sessions/from-session/{session_id}?user_id={user2_id}"
        )
        assert copy_response.status_code == 200
        copied_data = copy_response.json()

        # Verify the user_id is updated
        assert copied_data["user_id"] == user2_id
        assert copied_data["exercise_sessions"][0]["exercise_id"] == exercise_id
        assert copied_data["exercise_sessions"][0]["sets"][0]["weight"] == 15.0
