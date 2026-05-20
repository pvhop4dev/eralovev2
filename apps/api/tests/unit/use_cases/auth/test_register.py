"""Tests for Register Use Case."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.dtos.auth_dto import RegisterRequest
from application.use_cases.auth.register import RegisterUserUseCase
from domain.entities.user import User
from domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError


class TestRegisterUserUseCase:
    """Test suite for RegisterUserUseCase."""

    def _make_request(self, **overrides) -> RegisterRequest:
        defaults = {
            "email": "test@example.com",
            "password": "StrongPass1",
            "display_name": "Test User",
            "username": "testuser",
            "date_of_birth": date(2000, 3, 25),
            "gender": "male",
        }
        defaults.update(overrides)
        return RegisterRequest(**defaults)

    def _make_mock_user(self, **overrides) -> User:
        defaults = {
            "id": uuid4(),
            "email": "test@example.com",
            "password_hash": "$2b$12$fakehash",
            "display_name": "Test User",
            "username": "testuser",
        }
        defaults.update(overrides)
        return User(**defaults)

    @pytest.mark.asyncio
    async def test_register_success(self):
        user_repo = AsyncMock()
        user_repo.email_exists.return_value = False
        user_repo.username_exists.return_value = False
        user_repo.create.return_value = self._make_mock_user()

        redis = AsyncMock()
        redis.setex = AsyncMock()

        use_case = RegisterUserUseCase(
            user_repo=user_repo,
            redis_client=redis,
            email_sender=None,
        )

        auth_response, refresh_token = await use_case.execute(self._make_request())

        assert auth_response.user.email == "test@example.com"
        assert auth_response.access_token is not None
        assert len(auth_response.access_token) > 0
        assert refresh_token is not None
        user_repo.create.assert_called_once()
        redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self):
        user_repo = AsyncMock()
        user_repo.email_exists.return_value = True

        redis = AsyncMock()

        use_case = RegisterUserUseCase(
            user_repo=user_repo,
            redis_client=redis,
        )

        with pytest.raises(EmailAlreadyExistsError):
            await use_case.execute(self._make_request())

        user_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_duplicate_username_raises(self):
        user_repo = AsyncMock()
        user_repo.email_exists.return_value = False
        user_repo.username_exists.return_value = True

        redis = AsyncMock()

        use_case = RegisterUserUseCase(
            user_repo=user_repo,
            redis_client=redis,
        )

        with pytest.raises(UsernameAlreadyExistsError):
            await use_case.execute(self._make_request())

        user_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_weak_password_raises(self):
        """Password validation is done by Password VO — no uppercase."""
        from domain.exceptions import ValidationError

        user_repo = AsyncMock()
        user_repo.email_exists.return_value = False
        user_repo.username_exists.return_value = False

        redis = AsyncMock()

        use_case = RegisterUserUseCase(
            user_repo=user_repo,
            redis_client=redis,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(self._make_request(password="weakpassword"))

    @pytest.mark.asyncio
    async def test_register_normalizes_email(self):
        user_repo = AsyncMock()
        user_repo.email_exists.return_value = False
        user_repo.username_exists.return_value = False
        user_repo.create.return_value = self._make_mock_user()

        redis = AsyncMock()
        redis.setex = AsyncMock()

        use_case = RegisterUserUseCase(
            user_repo=user_repo,
            redis_client=redis,
            email_sender=None,
        )

        await use_case.execute(self._make_request(email="TeSt@EXAMPLE.COM"))

        # The create call should have a lowercased email
        call_args = user_repo.create.call_args[0][0]
        assert call_args.email == "test@example.com"
