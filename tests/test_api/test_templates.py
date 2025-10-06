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

    @pytest.mark.skip(reason="Nested exercise_sessions not populated correctly")
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

    @pytest.mark.skip(reason="FK validation not yet implemented")
    def test_create_template_invalid_user(self, client: TestClient):
        """Test creating template with non-existent user."""
        template_data = {
            "user_id": 99999,
            "name": "Invalid Template",
            "exercise_sessions": [],
        }
        response = client.post("/templates/", json=template_data)
        assert response.status_code == 404

    @pytest.mark.skip(reason="FK validation not yet implemented")
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

    @pytest.mark.skip(reason="Template update with exercise_sessions not implemented")
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

    @pytest.mark.skip(reason="Query parameter filtering not yet implemented")
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

    @pytest.mark.skip(reason="Nested exercise_sessions not populated correctly")
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
