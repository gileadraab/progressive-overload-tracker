"""Integration tests for templates API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestTemplatesAPI:
    """Test cases for /templates endpoints."""

    def test_create_template_simple(self, client: TestClient):
        """Test creating a simple template without exercises."""
        # Create user first
        user_response = client.post("/users/", json={"username": "templateuser"})
        user_id = user_response.json()["id"]

        # Create template
        template_data = {
            "user_id": user_id,
            "name": "Upper Body Workout",
            "exercise_sessions": [],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert data["name"] == "Upper Body Workout"
        assert "id" in data
        assert data["exercise_sessions"] == []

    def test_create_template_with_exercises(self, client: TestClient):
        """Test creating a template with exercises."""
        # Create user
        user_response = client.post("/users/", json={"username": "templateexuser"})
        user_id = user_response.json()["id"]

        # Create exercises
        exercise1 = client.post(
            "/exercises/", json={"name": "Bench Press", "category": "chest", "equipment": "barbell"}
        ).json()
        exercise2 = client.post(
            "/exercises/", json={"name": "Dumbbell Flyes", "category": "chest", "equipment": "dumbbell"}
        ).json()

        # Create template with exercises
        template_data = {
            "user_id": user_id,
            "name": "Chest Day",
            "exercise_sessions": [
                {"exercise_id": exercise1["id"]},
                {"exercise_id": exercise2["id"]},
            ],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chest Day"
        assert len(data["exercise_sessions"]) == 2
        assert data["exercise_sessions"][0]["exercise"]["id"] == exercise1["id"]
        assert data["exercise_sessions"][1]["exercise"]["id"] == exercise2["id"]

    def test_create_template_invalid_user(self, client: TestClient):
        """Test creating template with non-existent user."""
        template_data = {
            "user_id": 99999,
            "name": "Invalid Template",
            "exercise_sessions": [],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 404

    def test_create_template_invalid_exercise(self, client: TestClient):
        """Test creating template with non-existent exercise."""
        # Create user
        user_response = client.post("/users/", json={"username": "badtemplateuser"})
        user_id = user_response.json()["id"]

        # Try to create template with invalid exercise
        template_data = {
            "user_id": user_id,
            "name": "Bad Template",
            "exercise_sessions": [{"exercise_id": 99999}],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 404

    def test_create_template_missing_name(self, client: TestClient):
        """Test creating template without name."""
        # Create user
        user_response = client.post("/users/", json={"username": "nonameusertemplate"})
        user_id = user_response.json()["id"]

        template_data = {"user_id": user_id, "exercise_sessions": []}
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 422

    def test_get_all_templates(self, client: TestClient):
        """Test retrieving all templates."""
        # Create user
        user_response = client.post("/users/", json={"username": "alltemplatesuser"})
        user_id = user_response.json()["id"]

        # Create multiple templates
        for i in range(3):
            template_data = {
                "user_id": user_id,
                "name": f"Template {i}",
                "exercise_sessions": [],
            }
            client.post("/templates/", json=template_data)

        response = client.get("/templates/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_template_by_id(self, client: TestClient):
        """Test retrieving a specific template by ID."""
        # Create user and template
        user_response = client.post("/users/", json={"username": "gettemplateuser"})
        user_id = user_response.json()["id"]

        template_response = client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Get Template", "exercise_sessions": []},
        )
        template_id = template_response.json()["id"]

        # Get template
        response = client.get(f"/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["name"] == "Get Template"
        assert data["user_id"] == user_id

    def test_get_template_not_found(self, client: TestClient):
        """Test retrieving non-existent template."""
        response = client.get("/templates/99999")
        assert response.status_code == 404

    def test_update_template(self, client: TestClient):
        """Test updating a template."""
        # Create user
        user_response = client.post("/users/", json={"username": "updatetemplateuser"})
        user_id = user_response.json()["id"]

        # Create template
        template_response = client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Old Template Name", "exercise_sessions": []},
        )
        template_id = template_response.json()["id"]

        # Update template
        update_data = {
            "user_id": user_id,
            "name": "New Template Name",
            "exercise_sessions": [],
        }
        response = client.put(f"/templates/{template_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Template Name"

    def test_update_template_add_exercises(self, client: TestClient):
        """Test updating a template to add exercises."""
        # Create user
        user_response = client.post("/users/", json={"username": "addexuser"})
        user_id = user_response.json()["id"]

        # Create template without exercises
        template_response = client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Empty Template", "exercise_sessions": []},
        )
        template_id = template_response.json()["id"]

        # Create exercise
        exercise = client.post(
            "/exercises/", json={"name": "Squat", "category": "legs", "equipment": "barbell"}
        ).json()

        # Update template to add exercise
        update_data = {
            "user_id": user_id,
            "name": "Updated Template",
            "exercise_sessions": [{"exercise_id": exercise["id"]}],
        }
        response = client.put(f"/templates/{template_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["exercise_sessions"]) == 1

    def test_update_template_not_found(self, client: TestClient):
        """Test updating non-existent template."""
        # Create user for the update data
        user_response = client.post("/users/", json={"username": "ghosttemplateuser"})
        user_id = user_response.json()["id"]

        update_data = {
            "user_id": user_id,
            "name": "Ghost Template",
            "exercise_sessions": [],
        }
        response = client.put("/templates/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_template(self, client: TestClient):
        """Test deleting a template."""
        # Create user and template
        user_response = client.post("/users/", json={"username": "deletetemplateuser"})
        user_id = user_response.json()["id"]

        template_response = client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Delete Me", "exercise_sessions": []},
        )
        template_id = template_response.json()["id"]

        # Delete template
        response = client.delete(f"/templates/{template_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_template_not_found(self, client: TestClient):
        """Test deleting non-existent template."""
        response = client.delete("/templates/99999")
        assert response.status_code == 404

    def test_filter_templates_by_user(self, client: TestClient):
        """Test filtering templates by user_id."""
        # Create two users
        user1 = client.post("/users/", json={"username": "templatefilteruser1"}).json()
        user2 = client.post("/users/", json={"username": "templatefilteruser2"}).json()

        # Create templates for each user
        client.post(
            "/templates/",
            json={"user_id": user1["id"], "name": "User1 Template 1", "exercise_sessions": []},
        )
        client.post(
            "/templates/",
            json={"user_id": user1["id"], "name": "User1 Template 2", "exercise_sessions": []},
        )
        client.post(
            "/templates/",
            json={"user_id": user2["id"], "name": "User2 Template", "exercise_sessions": []},
        )

        # Filter by user1
        response = client.get(f"/templates/?user_id={user1['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(t["user_id"] == user1["id"] for t in data)

    def test_filter_templates_by_name(self, client: TestClient):
        """Test filtering templates by name."""
        # Create user
        user_response = client.post("/users/", json={"username": "namesearchuser"})
        user_id = user_response.json()["id"]

        # Create templates with different names
        client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Push Workout", "exercise_sessions": []},
        )
        client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Pull Workout", "exercise_sessions": []},
        )
        client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Leg Workout", "exercise_sessions": []},
        )

        # Search by name
        response = client.get("/templates/?name=Push")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("Push" in t["name"] for t in data)

    def test_pagination_skip_limit(self, client: TestClient):
        """Test pagination with skip and limit."""
        # Create user
        user_response = client.post("/users/", json={"username": "paginationtemplateuser"})
        user_id = user_response.json()["id"]

        # Create multiple templates
        for i in range(10):
            client.post(
                "/templates/",
                json={"user_id": user_id, "name": f"Template {i}", "exercise_sessions": []},
            )

        # Test pagination
        response = client.get("/templates/?skip=5&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_template_with_multiple_exercises(self, client: TestClient):
        """Test creating template with many exercises."""
        # Create user
        user_response = client.post("/users/", json={"username": "manyexuser"})
        user_id = user_response.json()["id"]

        # Create exercises
        exercise_ids = []
        for i in range(5):
            exercise = client.post(
                "/exercises/",
                json={
                    "name": f"Exercise {i}",
                    "category": "chest",
                    "equipment": "barbell",
                },
            ).json()
            exercise_ids.append(exercise["id"])

        # Create template with all exercises
        template_data = {
            "user_id": user_id,
            "name": "Full Body Template",
            "exercise_sessions": [{"exercise_id": ex_id} for ex_id in exercise_ids],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 201
        data = response.json()
        assert len(data["exercise_sessions"]) == 5

    def test_create_template_empty_name(self, client: TestClient):
        """Test creating template with empty name."""
        # Create user
        user_response = client.post("/users/", json={"username": "emptynameuser"})
        user_id = user_response.json()["id"]

        template_data = {"user_id": user_id, "name": "", "exercise_sessions": []}
        response = client.post("/templates/", json=template_data)
        # Should fail validation
        assert response.status_code == 422

    # Template Instantiation Workflow Tests

    def test_create_session_from_template(self, client: TestClient):
        """Test getting session structure from a template."""
        # Create user
        user_response = client.post("/users/", json={"username": "instantiateuser"})
        user_id = user_response.json()["id"]

        # Create exercises
        exercise1 = client.post(
            "/exercises/", json={"name": "Deadlift", "category": "back", "equipment": "barbell"}
        ).json()
        exercise2 = client.post(
            "/exercises/", json={"name": "Row", "category": "back", "equipment": "dumbbell"}
        ).json()

        # Create template with exercises
        template_data = {
            "user_id": user_id,
            "name": "Back Day Template",
            "exercise_sessions": [
                {"exercise_id": exercise1["id"]},
                {"exercise_id": exercise2["id"]},
            ],
        }
        template_response = client.post("/templates/", json=template_data)
        template_id = template_response.json()["id"]

        # Get session structure from template
        response = client.get(f"/sessions/from-template/{template_id}?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify session structure
        assert data["user_id"] == user_id
        assert data["date"] is None  # Default
        assert len(data["exercise_sessions"]) == 2
        assert data["exercise_sessions"][0]["exercise_id"] == exercise1["id"]
        assert data["exercise_sessions"][0]["sets"] == []  # Template has no sets
        assert data["exercise_sessions"][1]["exercise_id"] == exercise2["id"]
        assert data["exercise_sessions"][1]["sets"] == []

    def test_create_session_from_template_invalid_template(self, client: TestClient):
        """Test getting session from non-existent template."""
        # Create user
        user_response = client.post("/users/", json={"username": "badtemplateinstuser"})
        user_id = user_response.json()["id"]

        response = client.get(f"/sessions/from-template/99999?user_id={user_id}")
        assert response.status_code == 404

    def test_create_session_from_template_invalid_user(self, client: TestClient):
        """Test getting session from template with invalid user."""
        # Create user and template
        user_response = client.post("/users/", json={"username": "templateowneruser"})
        user_id = user_response.json()["id"]

        template_response = client.post(
            "/templates/",
            json={"user_id": user_id, "name": "Test Template", "exercise_sessions": []},
        )
        template_id = template_response.json()["id"]

        # Try with non-existent user
        response = client.get(f"/sessions/from-template/{template_id}?user_id=99999")
        assert response.status_code == 404

    def test_create_template_from_session(self, client: TestClient):
        """Test creating a template from an existing session."""
        # Create user
        user_response = client.post("/users/", json={"username": "sessiontotemplateuser"})
        user_id = user_response.json()["id"]

        # Create exercises
        exercise1 = client.post(
            "/exercises/", json={"name": "Overhead Press", "category": "shoulders", "equipment": "barbell"}
        ).json()
        exercise2 = client.post(
            "/exercises/", json={"name": "Lateral Raise", "category": "shoulders", "equipment": "dumbbell"}
        ).json()

        # Create session with exercises and sets
        session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise1["id"],
                    "sets": [
                        {"weight": 60, "reps": 8, "unit": "kg"},
                        {"weight": 60, "reps": 7, "unit": "kg"},
                    ],
                },
                {
                    "exercise_id": exercise2["id"],
                    "sets": [
                        {"weight": 15, "reps": 12, "unit": "kg"},
                    ],
                },
            ],
        }
        session_response = client.post("/sessions/", json=session_data)
        session_id = session_response.json()["id"]

        # Create template from session
        response = client.post(
            f"/templates/from-session/{session_id}?name=My Shoulder Day&user_id={user_id}"
        )
        assert response.status_code == 201
        data = response.json()

        # Verify template
        assert data["name"] == "My Shoulder Day"
        assert data["user_id"] == user_id
        assert len(data["exercise_sessions"]) == 2
        # Templates should have exercises but not sets
        assert data["exercise_sessions"][0]["exercise"]["id"] == exercise1["id"]
        assert data["exercise_sessions"][1]["exercise"]["id"] == exercise2["id"]

    def test_create_template_from_session_invalid_session(self, client: TestClient):
        """Test creating template from non-existent session."""
        # Create user
        user_response = client.post("/users/", json={"username": "badsessiontemplateuser"})
        user_id = user_response.json()["id"]

        response = client.post(
            f"/templates/from-session/99999?name=Bad Template&user_id={user_id}"
        )
        assert response.status_code == 404

    def test_create_template_from_session_invalid_user(self, client: TestClient):
        """Test creating template from session with invalid user."""
        # Create user and session
        user_response = client.post("/users/", json={"username": "sessionowneruser"})
        user_id = user_response.json()["id"]

        session_response = client.post(
            "/sessions/",
            json={"user_id": user_id, "exercise_sessions": []},
        )
        session_id = session_response.json()["id"]

        # Try with non-existent user
        response = client.post(
            f"/templates/from-session/{session_id}?name=Test&user_id=99999"
        )
        assert response.status_code == 404

    def test_full_template_workflow(self, client: TestClient):
        """Test complete workflow: create template → instantiate → create session → save as template."""
        # Create user
        user_response = client.post("/users/", json={"username": "workflowuser"})
        user_id = user_response.json()["id"]

        # Create exercise
        exercise = client.post(
            "/exercises/", json={"name": "Bicep Curl", "category": "arms", "equipment": "dumbbell"}
        ).json()

        # 1. Create original template
        template_response = client.post(
            "/templates/",
            json={
                "user_id": user_id,
                "name": "Arm Day Original",
                "exercise_sessions": [{"exercise_id": exercise["id"]}],
            },
        )
        original_template_id = template_response.json()["id"]

        # 2. Get session structure from template
        session_structure = client.get(
            f"/sessions/from-template/{original_template_id}?user_id={user_id}"
        ).json()

        # 3. Add sets to session structure
        session_structure["exercise_sessions"][0]["sets"] = [
            {"weight": 20, "reps": 12, "unit": "kg"},
            {"weight": 20, "reps": 10, "unit": "kg"},
        ]

        # 4. Create session
        session_response = client.post("/sessions/", json=session_structure)
        session_id = session_response.json()["id"]
        assert session_response.status_code == 201

        # 5. Save session as new template
        new_template_response = client.post(
            f"/templates/from-session/{session_id}?name=Arm Day Favorite&user_id={user_id}"
        )
        assert new_template_response.status_code == 201
        new_template = new_template_response.json()

        # Verify we have two different templates
        assert new_template["id"] != original_template_id
        assert new_template["name"] == "Arm Day Favorite"
        assert len(new_template["exercise_sessions"]) == 1
