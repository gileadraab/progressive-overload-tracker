"""End-to-end integration tests for complete workout workflows."""

from fastapi.testclient import TestClient


class TestCompleteWorkoutFlow:
    """Test complete end-to-end workflows that span multiple endpoints."""

    def test_progressive_overload_complete_workflow(self, client: TestClient):
        """
        Test the complete progressive overload workflow:
        1. Create first workout session
        2. Next week - copy previous workout
        3. Get exercise history for context
        4. Create improved session with higher weights
        5. Verify progression in history
        """
        # Setup: Create user and exercise
        user_response = client.post(
            "/users/", json={"username": "athlete", "display_name": "Pro Athlete"}
        )
        user_id = user_response.json()["id"]

        exercise_response = client.post(
            "/exercises/",
            json={
                "name": "Barbell Bench Press",
                "category": "chest",
                "equipment": "barbell",
            },
        )
        exercise_id = exercise_response.json()["id"]

        # Week 1: Create first workout session
        week1_session_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 100.0, "reps": 10, "unit": "kg"},
                        {"weight": 100.0, "reps": 9, "unit": "kg"},
                        {"weight": 100.0, "reps": 8, "unit": "kg"},
                    ],
                }
            ],
        }
        week1_response = client.post("/sessions/", json=week1_session_data)
        assert week1_response.status_code == 201
        week1_session = week1_response.json()
        week1_session_id = week1_session["id"]

        # Verify week 1 session was created correctly
        assert week1_session["user_id"] == user_id
        assert len(week1_session["exercise_sessions"]) == 1
        assert len(week1_session["exercise_sessions"][0]["sets"]) == 3

        # Week 2: Copy previous workout
        copy_response = client.get(
            f"/sessions/from-session/{week1_session_id}?user_id={user_id}"
        )
        assert copy_response.status_code == 200
        week2_template = copy_response.json()

        # Verify copied data structure
        assert week2_template["user_id"] == user_id
        assert len(week2_template["exercise_sessions"]) == 1
        assert week2_template["exercise_sessions"][0]["exercise_id"] == exercise_id
        assert len(week2_template["exercise_sessions"][0]["sets"]) == 3

        # Get exercise history to see what to aim for
        history_response = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        )
        assert history_response.status_code == 200
        history_data = history_response.json()

        # Verify history shows week 1 data
        assert history_data["exercise_id"] == exercise_id
        assert history_data["last_performed"] is not None
        assert history_data["last_performed"]["max_weight"] == 100.0
        assert (
            history_data["last_performed"]["total_volume"] == 2700
        )  # 100*10+100*9+100*8
        assert history_data["personal_best"] is not None
        assert history_data["personal_best"]["weight"] == 100.0
        assert history_data["personal_best"]["reps"] == 10

        # Check progression suggestion
        suggestion = history_data["progression_suggestion"]
        assert suggestion is not None
        assert suggestion["recommended_weight"] == 102.5  # +2.5kg increment
        assert "increase weight" in suggestion["rationale"].lower()

        # User applies progressive overload based on suggestion
        for set_data in week2_template["exercise_sessions"][0]["sets"]:
            set_data["weight"] = suggestion["recommended_weight"]

        # Create week 2 session with improved weights
        week2_response = client.post("/sessions/", json=week2_template)
        assert week2_response.status_code == 201
        week2_session = week2_response.json()
        week2_session_id = week2_session["id"]

        # Verify week 2 session is a new session (not modifying week 1)
        assert week2_session_id != week1_session_id
        assert week2_session["exercise_sessions"][0]["sets"][0]["weight"] == 102.5
        assert week2_session["exercise_sessions"][0]["sets"][1]["weight"] == 102.5
        assert week2_session["exercise_sessions"][0]["sets"][2]["weight"] == 102.5

        # Verify progression by checking updated history
        final_history_response = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        )
        assert final_history_response.status_code == 200
        final_history = final_history_response.json()

        # Last performed should now be week 2
        assert final_history["last_performed"]["max_weight"] == 102.5
        assert final_history["last_performed"]["total_volume"] == 2767.5  # 102.5*27

        # Personal best should be updated (higher estimated 1RM)
        assert final_history["personal_best"]["weight"] == 102.5
        assert (
            final_history["personal_best"]["estimated_1rm"]
            > history_data["personal_best"]["estimated_1rm"]
        )

        # Verify we have 2 sessions in history
        assert len(final_history["recent_sessions"]) == 2

    def test_template_to_session_workflow(self, client: TestClient):
        """
        Test creating a reusable workout template and using it:
        1. Create workout template
        2. Instantiate session from template
        3. Modify and create actual session
        4. Save modified session back as new template
        """
        # Setup
        user_response = client.post("/users/", json={"username": "templateuser"})
        user_id = user_response.json()["id"]

        # Create multiple exercises for a complete workout
        squat = client.post(
            "/exercises/",
            json={"name": "Squat", "category": "legs", "equipment": "barbell"},
        ).json()
        deadlift = client.post(
            "/exercises/",
            json={"name": "Deadlift", "category": "back", "equipment": "barbell"},
        ).json()
        leg_press = client.post(
            "/exercises/",
            json={"name": "Leg Press", "category": "legs", "equipment": "machine"},
        ).json()

        # Create a "Leg Day" template
        template_data = {
            "name": "Leg Day - Heavy",
            "user_id": user_id,
            "exercise_sessions": [
                {"exercise_id": squat["id"], "sets": []},
                {"exercise_id": deadlift["id"], "sets": []},
                {"exercise_id": leg_press["id"], "sets": []},
            ],
        }
        template_response = client.post("/templates/", json=template_data)
        assert template_response.status_code == 201
        template_id = template_response.json()["id"]

        # Instantiate session from template
        session_from_template = client.get(
            f"/sessions/from-template/{template_id}?user_id={user_id}"
        )
        assert session_from_template.status_code == 200
        session_data = session_from_template.json()

        # User adds actual sets for today's workout
        session_data["exercise_sessions"][0]["sets"] = [
            {"weight": 140.0, "reps": 5, "unit": "kg"},
            {"weight": 140.0, "reps": 5, "unit": "kg"},
            {"weight": 140.0, "reps": 5, "unit": "kg"},
        ]
        session_data["exercise_sessions"][1]["sets"] = [
            {"weight": 180.0, "reps": 5, "unit": "kg"},
            {"weight": 180.0, "reps": 3, "unit": "kg"},
        ]
        session_data["exercise_sessions"][2]["sets"] = [
            {"weight": 20.0, "reps": 12, "unit": "stacks"},
            {"weight": 20.0, "reps": 10, "unit": "stacks"},
        ]

        # Create actual session
        session_response = client.post("/sessions/", json=session_data)
        assert session_response.status_code == 201
        session_id = session_response.json()["id"]

        # Verify session was created with all exercises and sets
        get_session = client.get(f"/sessions/{session_id}")
        saved_session = get_session.json()
        assert len(saved_session["exercise_sessions"]) == 3
        assert len(saved_session["exercise_sessions"][0]["sets"]) == 3
        assert len(saved_session["exercise_sessions"][1]["sets"]) == 2
        assert len(saved_session["exercise_sessions"][2]["sets"]) == 2

        # User had a great workout, save it as a new template
        new_template_response = client.post(
            f"/templates/from-session/{session_id}?user_id={user_id}&name=Leg Day - PR Day"
        )
        assert new_template_response.status_code == 201
        new_template = new_template_response.json()
        assert new_template["name"] == "Leg Day - PR Day"
        assert len(new_template["exercise_sessions"]) == 3

    def test_multi_week_progression_with_history(self, client: TestClient):
        """
        Test realistic multi-week progressive overload:
        1. Week 1: First workout
        2. Week 2: Copy + increase weight
        3. Week 3: Copy + increase reps
        4. Week 4: Copy + increase weight again
        5. Verify complete history tracking
        """
        # Setup
        user_response = client.post("/users/", json={"username": "progressionuser"})
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

        # Week 1: Starting workout
        week1_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 50.0, "reps": 8, "unit": "kg"},
                        {"weight": 50.0, "reps": 8, "unit": "kg"},
                        {"weight": 50.0, "reps": 7, "unit": "kg"},
                    ],
                }
            ],
        }
        week1_session = client.post("/sessions/", json=week1_data).json()

        # Week 2: Same weight, more reps
        week2_template = client.get(
            f"/sessions/from-session/{week1_session['id']}?user_id={user_id}"
        ).json()
        week2_template["exercise_sessions"][0]["sets"][0]["reps"] = 10
        week2_template["exercise_sessions"][0]["sets"][1]["reps"] = 10
        week2_template["exercise_sessions"][0]["sets"][2]["reps"] = 9
        week2_session = client.post("/sessions/", json=week2_template).json()

        # Check history after week 2
        history_week2 = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        ).json()
        assert len(history_week2["recent_sessions"]) == 2
        assert history_week2["progression_suggestion"]["recommended_weight"] == 52.5

        # Week 3: Increase weight as suggested
        week3_template = client.get(
            f"/sessions/from-session/{week2_session['id']}?user_id={user_id}"
        ).json()
        for set_data in week3_template["exercise_sessions"][0]["sets"]:
            set_data["weight"] = 52.5
            set_data["reps"] = 8  # Reset reps with heavier weight
        week3_session = client.post("/sessions/", json=week3_template).json()

        # Week 4: More reps at 52.5kg
        week4_template = client.get(
            f"/sessions/from-session/{week3_session['id']}?user_id={user_id}"
        ).json()
        week4_template["exercise_sessions"][0]["sets"][0]["reps"] = 10
        week4_template["exercise_sessions"][0]["sets"][1]["reps"] = 10
        week4_template["exercise_sessions"][0]["sets"][2]["reps"] = 10
        client.post("/sessions/", json=week4_template)

        # Final history check
        final_history = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        ).json()

        # Should have 4 sessions
        assert len(final_history["recent_sessions"]) == 4

        # Personal best should be from week 4 (52.5kg x 10 reps)
        assert final_history["personal_best"]["weight"] == 52.5
        assert final_history["personal_best"]["reps"] == 10

        # Should suggest weight increase again
        assert final_history["progression_suggestion"]["recommended_weight"] == 55.0

        # Volume should show progression
        assert final_history["last_performed"]["total_volume"] > week1_session[
            "exercise_sessions"
        ][0]["sets"][0]["weight"] * sum(
            s["reps"] for s in week1_session["exercise_sessions"][0]["sets"]
        )

    def test_bodyweight_exercise_progression(self, client: TestClient):
        """
        Test progressive overload for bodyweight exercises:
        1. Start with bodyweight pull-ups
        2. Progress by adding reps
        3. Add weight (weighted pull-ups)
        4. Verify history tracks progression correctly
        """
        # Setup
        user_response = client.post("/users/", json={"username": "calisthenicsuser"})
        user_id = user_response.json()["id"]

        pullup_response = client.post(
            "/exercises/",
            json={"name": "Pull-ups", "category": "back", "equipment": "bodyweight"},
        )
        exercise_id = pullup_response.json()["id"]

        # Session 1: Bodyweight pull-ups
        session1_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": exercise_id,
                    "sets": [
                        {"weight": 0.0, "reps": 8, "unit": "kg"},
                        {"weight": 0.0, "reps": 7, "unit": "kg"},
                        {"weight": 0.0, "reps": 6, "unit": "kg"},
                    ],
                }
            ],
        }
        session1 = client.post("/sessions/", json=session1_data).json()

        # Session 2: More reps
        session2_template = client.get(
            f"/sessions/from-session/{session1['id']}?user_id={user_id}"
        ).json()
        session2_template["exercise_sessions"][0]["sets"][0]["reps"] = 10
        session2_template["exercise_sessions"][0]["sets"][1]["reps"] = 10
        session2_template["exercise_sessions"][0]["sets"][2]["reps"] = 9
        session2 = client.post("/sessions/", json=session2_template).json()

        # Check history - should suggest adding weight
        history_after_session2 = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        ).json()
        suggestion = history_after_session2["progression_suggestion"]
        # For bodyweight exercises at 0kg, suggestion should be meaningful
        assert suggestion is not None
        assert (
            suggestion["recommended_reps"] >= 10 or suggestion["recommended_weight"] > 0
        )

        # Session 3: Add weight (weighted pull-ups)
        session3_template = client.get(
            f"/sessions/from-session/{session2['id']}?user_id={user_id}"
        ).json()
        for set_data in session3_template["exercise_sessions"][0]["sets"]:
            set_data["weight"] = 5.0  # Add 5kg weight
            set_data["reps"] = 8  # Fewer reps with added weight
        client.post("/sessions/", json=session3_template)

        # Verify final history
        final_history = client.get(
            f"/exercises/{exercise_id}/history?user_id={user_id}"
        ).json()
        assert len(final_history["recent_sessions"]) == 3
        assert final_history["last_performed"]["max_weight"] == 5.0
        # Personal best depends on 1RM calculation, could be either session 2 or 3
        assert final_history["personal_best"] is not None

    def test_multi_exercise_session_with_individual_history(self, client: TestClient):
        """
        Test tracking multiple exercises in one session and their individual histories:
        1. Create session with 3 exercises
        2. Copy and progress each exercise differently
        3. Verify each exercise has independent history
        """
        # Setup
        user_response = client.post("/users/", json={"username": "fullworkoutuser"})
        user_id = user_response.json()["id"]

        # Create a push day workout
        bench = client.post(
            "/exercises/",
            json={"name": "Bench Press", "category": "chest", "equipment": "barbell"},
        ).json()
        incline = client.post(
            "/exercises/",
            json={
                "name": "Incline Press",
                "category": "chest",
                "equipment": "dumbbell",
            },
        ).json()
        tricep = client.post(
            "/exercises/",
            json={
                "name": "Tricep Extension",
                "category": "arms",
                "equipment": "dumbbell",
            },
        ).json()

        # Week 1: Full push workout
        week1_data = {
            "user_id": user_id,
            "exercise_sessions": [
                {
                    "exercise_id": bench["id"],
                    "sets": [
                        {"weight": 80.0, "reps": 10, "unit": "kg"},
                        {"weight": 80.0, "reps": 9, "unit": "kg"},
                    ],
                },
                {
                    "exercise_id": incline["id"],
                    "sets": [
                        {"weight": 30.0, "reps": 10, "unit": "kg"},
                        {"weight": 30.0, "reps": 8, "unit": "kg"},
                    ],
                },
                {
                    "exercise_id": tricep["id"],
                    "sets": [
                        {"weight": 15.0, "reps": 12, "unit": "kg"},
                        {"weight": 15.0, "reps": 10, "unit": "kg"},
                    ],
                },
            ],
        }
        week1_session = client.post("/sessions/", json=week1_data).json()

        # Week 2: Copy and progress differently for each exercise
        week2_template = client.get(
            f"/sessions/from-session/{week1_session['id']}?user_id={user_id}"
        ).json()

        # Bench: increase weight
        for set_data in week2_template["exercise_sessions"][0]["sets"]:
            set_data["weight"] = 82.5

        # Incline: add a set
        week2_template["exercise_sessions"][1]["sets"].append(
            {"weight": 30.0, "reps": 8, "unit": "kg"}
        )

        # Tricep: increase reps
        for set_data in week2_template["exercise_sessions"][2]["sets"]:
            set_data["reps"] += 2

        client.post("/sessions/", json=week2_template)

        # Check individual exercise histories
        bench_history = client.get(
            f"/exercises/{bench['id']}/history?user_id={user_id}"
        ).json()
        incline_history = client.get(
            f"/exercises/{incline['id']}/history?user_id={user_id}"
        ).json()
        tricep_history = client.get(
            f"/exercises/{tricep['id']}/history?user_id={user_id}"
        ).json()

        # Each should have 2 sessions
        assert len(bench_history["recent_sessions"]) == 2
        assert len(incline_history["recent_sessions"]) == 2
        assert len(tricep_history["recent_sessions"]) == 2

        # Verify last performed is different for each
        assert bench_history["last_performed"]["max_weight"] == 82.5
        assert incline_history["last_performed"]["max_weight"] == 30.0
        assert len(incline_history["last_performed"]["sets"]) == 3
        assert tricep_history["last_performed"]["sets"][0]["reps"] == 14

        # Each should have independent progression suggestions
        assert bench_history["progression_suggestion"] is not None
        assert incline_history["progression_suggestion"] is not None
        assert tricep_history["progression_suggestion"] is not None
