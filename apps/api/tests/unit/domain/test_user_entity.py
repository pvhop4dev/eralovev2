"""Tests for User Entity."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from domain.entities.user import User
from domain.exceptions import AlreadyDeletedError, NotDeletedError


class TestUserEntity:
    """Test suite for User domain entity."""

    def test_create_user_with_defaults(self):
        user = User(email="test@example.com", display_name="Test User", username="testuser")
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.is_email_verified is False
        assert user.is_onboarded is False
        assert user.is_deleted is False
        assert user.is_active is False  # Not verified yet

    def test_zodiac_auto_calculated_from_dob(self):
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            date_of_birth=date(2000, 3, 25),
        )
        assert user.zodiac_sign == "Aries"

    def test_zodiac_capricorn_december(self):
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            date_of_birth=date(2000, 12, 25),
        )
        assert user.zodiac_sign == "Capricorn"

    def test_zodiac_capricorn_january(self):
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            date_of_birth=date(2000, 1, 10),
        )
        assert user.zodiac_sign == "Capricorn"

    def test_zodiac_not_calculated_when_no_dob(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.zodiac_sign is None

    def test_age_calculation(self):
        dob = date(2000, 1, 1)
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            date_of_birth=dob,
        )
        age = user.age
        assert age is not None
        assert age >= 25  # At least 25 as of 2025+

    def test_age_none_when_no_dob(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.age is None

    def test_verify_email(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.is_email_verified is False
        user.verify_email()
        assert user.is_email_verified is True

    def test_is_active_requires_verification(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.is_active is False
        user.verify_email()
        assert user.is_active is True

    def test_complete_onboarding(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        user.complete_onboarding(
            display_name="New Name",
            date_of_birth=date(1995, 6, 15),
            love_language="Words of Affirmation",
            avatar_url="https://s3.example.com/avatar.jpg",
        )
        assert user.is_onboarded is True
        assert user.display_name == "New Name"
        assert user.love_language == "Words of Affirmation"
        assert user.zodiac_sign == "Gemini"
        assert user.avatar_url == "https://s3.example.com/avatar.jpg"

    def test_soft_delete(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.is_deleted is False
        user.soft_delete()
        assert user.is_deleted is True
        assert user.deleted_at is not None

    def test_soft_delete_already_deleted_raises(self):
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            deleted_at=datetime.now(timezone.utc),
        )
        with pytest.raises(AlreadyDeletedError):
            user.soft_delete()

    def test_restore(self):
        user = User(
            email="a@b.com",
            display_name="Test",
            username="test",
            deleted_at=datetime.now(timezone.utc),
        )
        assert user.is_deleted is True
        user.restore()
        assert user.is_deleted is False
        assert user.deleted_at is None

    def test_restore_not_deleted_raises(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        with pytest.raises(NotDeletedError):
            user.restore()

    def test_update_last_login(self):
        user = User(email="a@b.com", display_name="Test", username="test")
        assert user.last_login_at is None
        user.update_last_login()
        assert user.last_login_at is not None

    def test_to_dict(self):
        user = User(
            id=uuid4(),
            email="test@example.com",
            display_name="Test",
            username="test",
        )
        d = user.to_dict()
        assert d["email"] == "test@example.com"
        assert d["display_name"] == "Test"
        assert "id" in d
        assert "password_hash" in d
