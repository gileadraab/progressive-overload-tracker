import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services import user_service


class TestGetUsers:
    """Test suite for get_users function."""

    def test_get_all_users(self, db_session: Session):
        """Test getting all users."""
        # Create sample users
        users = [
            User(username="user1", name="User One"),
            User(username="user2", name="User Two"),
            User(username="user3", name="User Three"),
        ]
        for user in users:
            db_session.add(user)
        db_session.commit()

        # Get all users
        result = user_service.get_users(db_session)
        assert len(result) == 3
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        assert result[2].username == "user3"

    def test_get_users_with_pagination(self, db_session: Session):
        """Test getting users with pagination."""
        # Create 5 users
        for i in range(5):
            user = User(username=f"user{i}", name=f"User {i}")
            db_session.add(user)
        db_session.commit()

        # Get first 2 users
        result = user_service.get_users(db_session, skip=0, limit=2)
        assert len(result) == 2

        # Get next 2 users
        result = user_service.get_users(db_session, skip=2, limit=2)
        assert len(result) == 2

        # Get last user
        result = user_service.get_users(db_session, skip=4, limit=2)
        assert len(result) == 1

    def test_get_users_empty_database(self, db_session: Session):
        """Test getting users from empty database."""
        result = user_service.get_users(db_session)
        assert result == []


class TestGetUser:
    """Test suite for get_user function."""

    def test_get_existing_user(self, db_session: Session):
        """Test getting an existing user by ID."""
        user = User(username="testuser", name="Test User")
        db_session.add(user)
        db_session.commit()

        result = user_service.get_user(user.id, db_session)
        assert result.id == user.id
        assert result.username == "testuser"
        assert result.name == "Test User"

    def test_get_nonexistent_user(self, db_session: Session):
        """Test getting a non-existent user raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestGetUserByUsername:
    """Test suite for get_user_by_username function."""

    def test_get_user_by_existing_username(self, db_session: Session):
        """Test getting a user by their username."""
        user = User(username="testuser", name="Test User")
        db_session.add(user)
        db_session.commit()

        result = user_service.get_user_by_username("testuser", db_session)
        assert result.id == user.id
        assert result.username == "testuser"
        assert result.name == "Test User"

    def test_get_user_by_nonexistent_username(self, db_session: Session):
        """Test getting a user by non-existent username raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_username("nonexistent", db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_get_user_by_username_case_sensitive(self, db_session: Session):
        """Test that username lookup is case-sensitive."""
        user = User(username="TestUser", name="Test User")
        db_session.add(user)
        db_session.commit()

        # Should find with exact case
        result = user_service.get_user_by_username("TestUser", db_session)
        assert result.username == "TestUser"

        # Should not find with different case
        with pytest.raises(HTTPException):
            user_service.get_user_by_username("testuser", db_session)


class TestCreateUser:
    """Test suite for create_user function."""

    def test_create_user_basic(self, db_session: Session):
        """Test creating a basic user."""
        user_data = UserCreate(username="testuser", name="Test User")

        result = user_service.create_user(user_data, db_session)
        assert result.id is not None
        assert result.username == "testuser"
        assert result.name == "Test User"

    def test_create_user_without_name(self, db_session: Session):
        """Test creating a user without name."""
        user_data = UserCreate(username="testuser")

        result = user_service.create_user(user_data, db_session)
        assert result.id is not None
        assert result.username == "testuser"
        assert result.name is None

    def test_create_user_duplicate_username(self, db_session: Session):
        """Test creating a user with duplicate username raises HTTPException."""
        user_data1 = UserCreate(username="testuser", name="User One")
        user_service.create_user(user_data1, db_session)

        user_data2 = UserCreate(username="testuser", name="User Two")
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(user_data2, db_session)
        assert exc_info.value.status_code == 400
        assert "already taken" in exc_info.value.detail.lower()

    def test_create_user_persisted(self, db_session: Session):
        """Test that created user is persisted to database."""
        user_data = UserCreate(username="testuser", name="Test User")

        created_user = user_service.create_user(user_data, db_session)

        # Verify it's in the database
        retrieved_user = db_session.get(User, created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"


class TestUpdateUser:
    """Test suite for update_user function."""

    def test_update_user_username(self, db_session: Session):
        """Test updating user username."""
        user = User(username="oldusername", name="Test User")
        db_session.add(user)
        db_session.commit()

        update_data = UserUpdate(username="newusername")
        result = user_service.update_user(user.id, update_data, db_session)

        assert result.id == user.id
        assert result.username == "newusername"
        assert result.name == "Test User"  # Unchanged

    def test_update_user_name(self, db_session: Session):
        """Test updating user name."""
        user = User(username="testuser", name="Old Name")
        db_session.add(user)
        db_session.commit()

        update_data = UserUpdate(name="New Name")
        result = user_service.update_user(user.id, update_data, db_session)

        assert result.id == user.id
        assert result.username == "testuser"  # Unchanged
        assert result.name == "New Name"

    def test_update_user_multiple_fields(self, db_session: Session):
        """Test updating multiple fields at once."""
        user = User(username="oldusername", name="Old Name")
        db_session.add(user)
        db_session.commit()

        update_data = UserUpdate(username="newusername", name="New Name")
        result = user_service.update_user(user.id, update_data, db_session)

        assert result.username == "newusername"
        assert result.name == "New Name"

    def test_update_user_to_taken_username(self, db_session: Session):
        """Test updating username to one that's already taken raises HTTPException."""
        user1 = User(username="user1", name="User One")
        user2 = User(username="user2", name="User Two")
        db_session.add_all([user1, user2])
        db_session.commit()

        update_data = UserUpdate(username="user2")
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(user1.id, update_data, db_session)
        assert exc_info.value.status_code == 400
        assert "already taken" in exc_info.value.detail.lower()

    def test_update_user_to_same_username(self, db_session: Session):
        """Test updating user to the same username (should succeed)."""
        user = User(username="testuser", name="Old Name")
        db_session.add(user)
        db_session.commit()

        # Update name but keep same username
        update_data = UserUpdate(username="testuser", name="New Name")
        result = user_service.update_user(user.id, update_data, db_session)

        assert result.username == "testuser"
        assert result.name == "New Name"

    def test_update_nonexistent_user(self, db_session: Session):
        """Test updating a non-existent user raises HTTPException."""
        update_data = UserUpdate(username="newusername")

        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(999, update_data, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_update_user_partial(self, db_session: Session):
        """Test partial update with exclude_unset."""
        user = User(username="testuser", name="Test User")
        db_session.add(user)
        db_session.commit()

        # Only update name, leave username unchanged
        update_data = UserUpdate(name="New Name")
        result = user_service.update_user(user.id, update_data, db_session)

        assert result.username == "testuser"
        assert result.name == "New Name"


class TestDeleteUser:
    """Test suite for delete_user function."""

    def test_delete_existing_user(self, db_session: Session):
        """Test deleting an existing user."""
        user = User(username="testuser", name="Test User")
        db_session.add(user)
        db_session.commit()
        user_id = user.id

        # Delete the user
        user_service.delete_user(user_id, db_session)

        # Verify it's deleted
        deleted_user = db_session.get(User, user_id)
        assert deleted_user is None

    def test_delete_nonexistent_user(self, db_session: Session):
        """Test deleting a non-existent user raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            user_service.delete_user(999, db_session)
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_user_returns_none(self, db_session: Session):
        """Test that delete_user returns None."""
        user = User(username="testuser", name="Test User")
        db_session.add(user)
        db_session.commit()

        result = user_service.delete_user(user.id, db_session)
        assert result is None
