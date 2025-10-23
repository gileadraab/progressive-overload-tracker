"""
Comprehensive workflow tests for the Progressive Overload Tracker.

These tests follow real user workflows from registration to account deletion,
focusing on the happy path that users will actually follow.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.enums import CategoryEnum, EquipmentEnum
from src.models.exercise import Exercise
from src.models.template import Template


def test_complete_user_workflow(client: TestClient, db_session: Session):
    """
    Complete user workflow from registration to account deletion.
    Tests the happy path that 90% of users will follow.

    Flow:
    1. Populate DB with 4 new exercises (seed data)
    2. Create a global template with 4 exercises (seed data)
    3. User creates an account
    4. User logs in
    5. User creates a session: add 3 exercises, 3 sets each
    6. User creates a session from the global template
    7. User creates a custom template
    8. User starts a session from their custom template
    9. User changes the order of exercises in a session
    10. User copies a previous session
    11. User changes the order of sets
    12. User gets list with all their sessions
    13. User deletes their template
    14. User deletes their account
    """
    # ========== STEP 1: Populate DB with 4 exercises ==========
    exercises = [
        Exercise(
            name="Bench Press",
            category=CategoryEnum.CHEST,
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
        ),
        Exercise(
            name="Deadlift", category=CategoryEnum.BACK, equipment=EquipmentEnum.BARBELL
        ),
        Exercise(
            name="Overhead Press",
            category=CategoryEnum.SHOULDERS,
            equipment=EquipmentEnum.BARBELL,
        ),
    ]
    for exercise in exercises:
        db_session.add(exercise)
    db_session.commit()
    for exercise in exercises:
        db_session.refresh(exercise)

    exercise_ids = [ex.id for ex in exercises]

    # ========== STEP 2: Create a global template with 4 exercises ==========
    # Create a dummy admin user for the global template
    from src.models.user import User
    from src.services import auth_service

    admin_user = User(
        username="admin",
        email="admin@example.com",
        name="Admin User",
        password_hash=auth_service.hash_password("admin123456"),
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    global_template = Template(
        user_id=admin_user.id,
        name="Full Body Workout",
        description="A complete full body routine",
        is_global=True,
    )
    db_session.add(global_template)
    db_session.commit()
    db_session.refresh(global_template)

    # Add exercises to global template
    from src.models.exercise_session import ExerciseSession

    for idx, exercise_id in enumerate(exercise_ids):
        ex_session = ExerciseSession(
            template_id=global_template.id, exercise_id=exercise_id, order=idx + 1
        )
        db_session.add(ex_session)
    db_session.commit()

    # ========== STEP 3: User creates an account ==========
    register_response = client.post(
        "/auth/register",
        json={
            "username": "john_doe",
            "email": "john@example.com",
            "name": "John Doe",
            "password": "password12345",
        },
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    user_id = user_data["id"]
    assert user_data["username"] == "john_doe"
    assert user_data["email"] == "john@example.com"

    # ========== STEP 4: User logs in ==========
    login_response = client.post(
        "/auth/login",
        json={"email": "john@example.com", "password": "password12345"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    assert tokens["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {access_token}"}

    # ========== STEP 5: User creates a session with 3 exercises, 3 sets each ==========
    session1_data = {
        "user_id": user_id,
        "notes": "First workout session",
        "exercise_sessions": [
            {
                "exercise_id": exercise_ids[0],  # Bench Press
                "sets": [
                    {"weight": 60.0, "reps": 10, "unit": "kg"},
                    {"weight": 60.0, "reps": 9, "unit": "kg"},
                    {"weight": 60.0, "reps": 8, "unit": "kg"},
                ],
            },
            {
                "exercise_id": exercise_ids[1],  # Squat
                "sets": [
                    {"weight": 80.0, "reps": 10, "unit": "kg"},
                    {"weight": 80.0, "reps": 9, "unit": "kg"},
                    {"weight": 80.0, "reps": 8, "unit": "kg"},
                ],
            },
            {
                "exercise_id": exercise_ids[2],  # Deadlift
                "sets": [
                    {"weight": 100.0, "reps": 5, "unit": "kg"},
                    {"weight": 100.0, "reps": 5, "unit": "kg"},
                    {"weight": 100.0, "reps": 5, "unit": "kg"},
                ],
            },
        ],
    }
    create_session1_response = client.post(
        "/sessions/", json=session1_data, headers=headers
    )
    assert create_session1_response.status_code == 201
    session1 = create_session1_response.json()
    session1_id = session1["id"]
    assert len(session1["exercise_sessions"]) == 3

    # ========== STEP 6: User creates a session from the global template ==========
    get_template_response = client.get(
        f"/sessions/from-template/{global_template.id}?user_id={user_id}",
        headers=headers,
    )
    assert get_template_response.status_code == 200
    template_session_data = get_template_response.json()
    assert len(template_session_data["exercise_sessions"]) == 4

    # Create session from template
    create_session2_response = client.post(
        "/sessions/", json=template_session_data, headers=headers
    )
    assert create_session2_response.status_code == 201
    session2 = create_session2_response.json()
    assert len(session2["exercise_sessions"]) == 4

    # ========== STEP 7: User creates a template ==========
    create_template_response = client.post(
        "/templates/",
        json={
            "user_id": user_id,
            "name": "Upper Body Day",
            "description": "My custom upper body routine",
            "exercise_sessions": [
                {"exercise_id": exercise_ids[0]},  # Bench Press
                {"exercise_id": exercise_ids[3]},  # Overhead Press
            ],
        },
        headers=headers,
    )
    assert create_template_response.status_code == 201
    user_template = create_template_response.json()
    user_template_id = user_template["id"]
    assert user_template["name"] == "Upper Body Day"
    assert len(user_template["exercise_sessions"]) == 2

    # ========== STEP 8: User starts a session from his custom template ==========
    get_user_template_response = client.get(
        f"/sessions/from-template/{user_template_id}?user_id={user_id}",
        headers=headers,
    )
    assert get_user_template_response.status_code == 200
    user_template_session_data = get_user_template_response.json()

    create_session3_response = client.post(
        "/sessions/", json=user_template_session_data, headers=headers
    )
    assert create_session3_response.status_code == 201
    session3 = create_session3_response.json()
    session3_id = session3["id"]
    assert len(session3["exercise_sessions"]) == 2

    # ========== STEP 9: User changes the order of exercises in session ==========
    get_session3_response = client.get(f"/sessions/{session3_id}", headers=headers)
    assert get_session3_response.status_code == 200
    session3_details = get_session3_response.json()

    # Swap the order of the two exercises
    ex_sessions = session3_details["exercise_sessions"]
    reorder_data = {
        "exercise_sessions": [
            {"id": ex_sessions[0]["id"], "order": 2},
            {"id": ex_sessions[1]["id"], "order": 1},
        ]
    }
    reorder_response = client.patch(
        f"/sessions/{session3_id}/reorder", json=reorder_data, headers=headers
    )
    assert reorder_response.status_code == 200

    # Verify order changed
    get_session3_after_response = client.get(
        f"/sessions/{session3_id}", headers=headers
    )
    assert get_session3_after_response.status_code == 200
    session3_after = get_session3_after_response.json()
    assert session3_after["exercise_sessions"][0]["order"] == 1
    assert session3_after["exercise_sessions"][1]["order"] == 2

    # ========== STEP 10: User copies a previous session (1st one) ==========
    copy_session_response = client.get(
        f"/sessions/from-session/{session1_id}?user_id={user_id}", headers=headers
    )
    assert copy_session_response.status_code == 200
    copied_session_data = copy_session_response.json()

    create_session4_response = client.post(
        "/sessions/", json=copied_session_data, headers=headers
    )
    assert create_session4_response.status_code == 201
    session4 = create_session4_response.json()
    session4_id = session4["id"]

    # ========== STEP 11: User changes the order of sets ==========
    get_session4_response = client.get(f"/sessions/{session4_id}", headers=headers)
    assert get_session4_response.status_code == 200
    session4_details = get_session4_response.json()

    # Reorder sets in the first exercise
    first_ex_session = session4_details["exercise_sessions"][0]
    sets = first_ex_session["sets"]
    reorder_sets_data = {
        "exercise_sessions": [
            {
                "id": first_ex_session["id"],
                "sets": [
                    {"id": sets[2]["id"], "order": 1},
                    {"id": sets[1]["id"], "order": 2},
                    {"id": sets[0]["id"], "order": 3},
                ],
            }
        ]
    }
    reorder_sets_response = client.patch(
        f"/sessions/{session4_id}/reorder", json=reorder_sets_data, headers=headers
    )
    assert reorder_sets_response.status_code == 200

    # ========== STEP 12: User gets list with all his sessions ==========
    list_sessions_response = client.get("/sessions/", headers=headers)
    assert list_sessions_response.status_code == 200
    sessions_list = list_sessions_response.json()
    assert len(sessions_list) == 4  # 4 sessions created

    # ========== STEP 13: User deletes a template ==========
    delete_template_response = client.delete(
        f"/templates/{user_template_id}", headers=headers
    )
    assert delete_template_response.status_code == 204

    # Verify template deleted
    get_deleted_template_response = client.get(
        f"/templates/{user_template_id}", headers=headers
    )
    assert get_deleted_template_response.status_code == 404

    # ========== STEP 14: User deletes his account ==========
    delete_user_response = client.delete(f"/users/{user_id}", headers=headers)
    assert delete_user_response.status_code == 204

    # Verify user deleted
    get_deleted_user_response = client.get(f"/users/{user_id}", headers=headers)
    assert get_deleted_user_response.status_code == 404


def test_token_lifecycle(client: TestClient, db_session: Session):
    """
    Test JWT token generation and refresh.

    Ensures token lifecycle works correctly for keeping users logged in.
    """
    # Register user
    register_response = client.post(
        "/auth/register",
        json={
            "username": "jane_doe",
            "email": "jane@example.com",
            "name": "Jane Doe",
            "password": "securepass123",
        },
    )
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "jane@example.com", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Use access token to access protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    get_user_response = client.get("/users/", headers=headers)
    assert get_user_response.status_code == 200

    # Refresh token
    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    new_access_token = new_tokens["access_token"]

    # Use new access token
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    get_user_response2 = client.get("/users/", headers=new_headers)
    assert get_user_response2.status_code == 200

    # Test invalid refresh token
    invalid_refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": "invalid_token"}
    )
    assert invalid_refresh_response.status_code == 401


def test_exercise_history_and_progression(client: TestClient, db_session: Session):
    """
    Test progressive overload tracking (core feature).

    Creates multiple sessions with the same exercise, increasing weight,
    and verifies history shows PR and progression suggestions.
    """
    # Create exercise
    exercise = Exercise(
        name="Bench Press",
        category=CategoryEnum.CHEST,
        equipment=EquipmentEnum.BARBELL,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    # Register and login user
    register_response = client.post(
        "/auth/register",
        json={
            "username": "lifter",
            "email": "lifter@example.com",
            "name": "The Lifter",
            "password": "gainz123456",
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={"email": "lifter@example.com", "password": "gainz123456"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create 3 sessions with increasing weights
    session_data_1 = {
        "user_id": user_id,
        "notes": "Week 1",
        "exercise_sessions": [
            {
                "exercise_id": exercise.id,
                "sets": [
                    {"weight": 60.0, "reps": 10, "unit": "kg"},
                    {"weight": 60.0, "reps": 10, "unit": "kg"},
                    {"weight": 60.0, "reps": 10, "unit": "kg"},
                ],
            }
        ],
    }
    client.post("/sessions/", json=session_data_1, headers=headers)

    session_data_2 = {
        "user_id": user_id,
        "notes": "Week 2",
        "exercise_sessions": [
            {
                "exercise_id": exercise.id,
                "sets": [
                    {"weight": 62.5, "reps": 10, "unit": "kg"},
                    {"weight": 62.5, "reps": 10, "unit": "kg"},
                    {"weight": 62.5, "reps": 9, "unit": "kg"},
                ],
            }
        ],
    }
    client.post("/sessions/", json=session_data_2, headers=headers)

    session_data_3 = {
        "user_id": user_id,
        "notes": "Week 3",
        "exercise_sessions": [
            {
                "exercise_id": exercise.id,
                "sets": [
                    {"weight": 65.0, "reps": 10, "unit": "kg"},
                    {"weight": 65.0, "reps": 10, "unit": "kg"},
                    {"weight": 65.0, "reps": 10, "unit": "kg"},
                ],
            }
        ],
    }
    client.post("/sessions/", json=session_data_3, headers=headers)

    # Get exercise history
    history_response = client.get(
        f"/exercises/{exercise.id}/history?user_id={user_id}", headers=headers
    )
    assert history_response.status_code == 200
    history = history_response.json()

    # Verify history structure
    assert "last_performed" in history
    assert "personal_best" in history
    assert "recent_sessions" in history
    assert "progression_suggestion" in history

    # Verify last performed shows most recent session
    assert history["last_performed"]["sets"][0]["weight"] == 65.0

    # Verify personal best (highest estimated 1RM)
    assert history["personal_best"] is not None

    # Verify progression suggestion
    assert history["progression_suggestion"] is not None
    assert "recommended_weight" in history["progression_suggestion"]

    # Verify recent sessions
    assert len(history["recent_sessions"]) == 3


def test_authorization_boundaries(client: TestClient, db_session: Session):
    """
    Test users can't access each other's data.

    Ensures authorization boundaries work correctly.
    """
    # Create exercise
    exercise = Exercise(
        name="Squat", category=CategoryEnum.LEGS, equipment=EquipmentEnum.BARBELL
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    # Register user 1
    client.post(
        "/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "name": "User One",
            "password": "password123",
        },
    )
    login1 = client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "password123"}
    )
    user1_token = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {user1_token}"}

    # Register user 2
    client.post(
        "/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "name": "User Two",
            "password": "password123",
        },
    )
    login2 = client.post(
        "/auth/login", json={"email": "user2@example.com", "password": "password123"}
    )
    user2_token = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {user2_token}"}

    # Get user IDs from /users/ endpoint
    users1_response = client.get("/users/", headers=headers1)
    user1_actual_id = users1_response.json()[0]["id"]

    # User 1 creates a session
    session_data = {
        "user_id": user1_actual_id,
        "notes": "User 1's private session",
        "exercise_sessions": [
            {
                "exercise_id": exercise.id,
                "sets": [{"weight": 100.0, "reps": 5, "unit": "kg"}],
            }
        ],
    }
    create_session_response = client.post(
        "/sessions/", json=session_data, headers=headers1
    )
    assert create_session_response.status_code == 201
    session_id = create_session_response.json()["id"]

    # User 1 creates a template
    template_data = {
        "user_id": user1_actual_id,
        "name": "User 1's Template",
        "description": "Private template",
        "exercise_sessions": [{"exercise_id": exercise.id}],
    }
    create_template_response = client.post(
        "/templates/", json=template_data, headers=headers1
    )
    assert create_template_response.status_code == 201

    # User 2 tries to access User 1's session (should fail or not show it)
    get_user2_sessions = client.get("/sessions/", headers=headers2)
    assert get_user2_sessions.status_code == 200
    user2_sessions = get_user2_sessions.json()
    # User 2 should not see User 1's sessions
    assert len(user2_sessions) == 0

    # User 2 tries to access User 1's template (should fail or not show it)
    get_user2_templates = client.get("/templates/", headers=headers2)
    assert get_user2_templates.status_code == 200
    user2_templates = get_user2_templates.json()
    # User 2 should not see User 1's non-global templates
    user2_non_global_templates = [t for t in user2_templates if not t["is_global"]]
    assert len(user2_non_global_templates) == 0

    # User 2 tries to access User 1's data without authentication
    no_auth_session_response = client.get(f"/sessions/{session_id}")
    assert no_auth_session_response.status_code in [401, 403]


def test_global_template_readonly(client: TestClient, db_session: Session):
    """
    Test global templates cannot be modified by users.

    Ensures global templates remain read-only for regular users.
    """
    # Create exercise
    exercise = Exercise(
        name="Bench Press",
        category=CategoryEnum.CHEST,
        equipment=EquipmentEnum.BARBELL,
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)

    # Create admin user for global template
    from src.models.user import User
    from src.services import auth_service

    admin_user = User(
        username="admin",
        email="admin@example.com",
        name="Admin User",
        password_hash=auth_service.hash_password("admin123456"),
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # Create global template
    global_template = Template(
        user_id=admin_user.id,
        name="Global Workout",
        description="A global workout template",
        is_global=True,
    )
    db_session.add(global_template)
    db_session.commit()
    db_session.refresh(global_template)

    from src.models.exercise_session import ExerciseSession

    ex_session = ExerciseSession(
        template_id=global_template.id, exercise_id=exercise.id, order=1
    )
    db_session.add(ex_session)
    db_session.commit()

    # Register regular user
    register_response = client.post(
        "/auth/register",
        json={
            "username": "regular_user",
            "email": "regular@example.com",
            "name": "Regular User",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "regular@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # User can view global template
    get_template_response = client.get(
        f"/templates/{global_template.id}", headers=headers
    )
    assert get_template_response.status_code == 200

    # User tries to update global template (should fail)
    update_response = client.put(
        f"/templates/{global_template.id}",
        json={"name": "Modified Global Template"},
        headers=headers,
    )
    assert update_response.status_code in [403, 404]  # Forbidden or Not Found

    # User tries to delete global template (should fail)
    delete_response = client.delete(f"/templates/{global_template.id}", headers=headers)
    assert delete_response.status_code in [403, 404]  # Forbidden or Not Found

    # Verify global template still exists and unchanged
    verify_response = client.get(f"/templates/{global_template.id}", headers=headers)
    assert verify_response.status_code == 200
    template_data = verify_response.json()
    assert template_data["name"] == "Global Workout"
    assert template_data["is_global"] is True
