"""Utility functions for testing."""

from datetime import datetime
from typing import Any, Dict


def assert_exercise_response(
    response_data: Dict[str, Any],
    expected_name: str,
    expected_category: str,
    expected_equipment: str,
) -> None:
    """Assert that an exercise response matches expected values."""
    assert response_data["name"] == expected_name
    assert response_data["category"] == expected_category
    assert response_data["equipment"] == expected_equipment
    assert "id" in response_data
    assert "created_at" in response_data


def assert_user_response(
    response_data: Dict[str, Any],
    expected_username: str,
    expected_display_name: str = None,
) -> None:
    """Assert that a user response matches expected values."""
    assert response_data["username"] == expected_username
    if expected_display_name:
        assert response_data["display_name"] == expected_display_name
    assert "id" in response_data
    assert "created_at" in response_data


def assert_session_response(
    response_data: Dict[str, Any], expected_user_id: int, has_details: bool = False
) -> None:
    """Assert that a session response matches expected values."""
    assert response_data["user_id"] == expected_user_id
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data

    if has_details:
        assert "exercise_sessions" in response_data
        assert isinstance(response_data["exercise_sessions"], list)


def assert_template_response(
    response_data: Dict[str, Any],
    expected_name: str,
    expected_user_id: int,
    has_exercises: bool = False,
) -> None:
    """Assert that a template response matches expected values."""
    assert response_data["name"] == expected_name
    assert response_data["user_id"] == expected_user_id
    assert "id" in response_data
    assert "created_at" in response_data

    if has_exercises:
        assert "exercise_sessions" in response_data
        assert isinstance(response_data["exercise_sessions"], list)


def assert_set_response(
    response_data: Dict[str, Any],
    expected_weight: float,
    expected_reps: int,
    expected_unit: str,
) -> None:
    """Assert that a set response matches expected values."""
    assert response_data["weight"] == expected_weight
    assert response_data["reps"] == expected_reps
    assert response_data["unit"] == expected_unit
    assert "id" in response_data
    assert "order" in response_data
    assert "created_at" in response_data


def create_exercise_payload(
    name: str = "Test Exercise", category: str = "chest", equipment: str = "barbell"
) -> Dict[str, str]:
    """Create a valid exercise payload for testing."""
    return {"name": name, "category": category, "equipment": equipment}


def create_user_payload(
    username: str = "testuser", display_name: str = "Test User"
) -> Dict[str, str]:
    """Create a valid user payload for testing."""
    return {"username": username, "display_name": display_name}


def create_session_payload(user_id: int, notes: str = None) -> Dict[str, Any]:
    """Create a valid session payload for testing."""
    payload = {"user_id": user_id}
    if notes:
        payload["notes"] = notes
    return payload


def create_template_payload(
    user_id: int, name: str = "Test Template", description: str = None
) -> Dict[str, Any]:
    """Create a valid template payload for testing."""
    payload = {"user_id": user_id, "name": name}
    if description:
        payload["description"] = description
    return payload


def create_set_payload(
    session_id: int,
    exercise_session_id: int,
    weight: float = 100.0,
    reps: int = 10,
    unit: str = "kg",
    order: int = 1,
) -> Dict[str, Any]:
    """Create a valid set payload for testing."""
    return {
        "session_id": session_id,
        "exercise_session_id": exercise_session_id,
        "weight": weight,
        "reps": reps,
        "unit": unit,
        "order": order,
    }


def assert_datetime_recent(datetime_str: str, max_seconds_ago: int = 10) -> None:
    """Assert that a datetime string represents a recent timestamp."""
    dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    now = datetime.now(dt.tzinfo)
    diff = (now - dt).total_seconds()
    assert diff >= 0, f"Datetime is in the future: {datetime_str}"
    assert (
        diff <= max_seconds_ago
    ), f"Datetime is too old: {datetime_str} ({diff} seconds ago)"


def assert_pagination_response(response_data: Any, expected_min_items: int = 0) -> None:
    """Assert that a response contains pagination structure (list of items)."""
    assert isinstance(response_data, list), "Response should be a list"
    assert (
        len(response_data) >= expected_min_items
    ), f"Expected at least {expected_min_items} items"
