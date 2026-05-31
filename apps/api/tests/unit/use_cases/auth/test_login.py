"""Tests for Login Use Case."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.dtos.auth_dto import LoginRequest
from application.use_cases.auth.login import LoginUserUseCase
from domain.entities.user import User
from domain.exceptions import InvalidCredentialsError
from domain.value_objects.password import Password


class TestLoginUserUseCase:
    """Test suite for LoginUserUseCase."""

    def _make_user(self, email: str = "test@example.com", password: str = "StrongPass1") -> User:
        pw = Password.from_plaintext(password)
        return User(
            id=uuid4(),
            email=email,
            password_hash=pw.hashed_value,
            display_name="Test User",
            username="testuser",
        )

    @pytest.mark.asyncio
    async def test_login_success(self):
        user = self._make_user()
        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = user
        user_repo.update.return_value = user
        token_repo = AsyncMock()

        use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
        dto = LoginRequest(email="test@example.com", password="StrongPass1")
        auth_response, refresh_token = await use_case.execute(dto)

        assert auth_response.user.email == "test@example.com"
        assert auth_response.access_token is not None
        assert refresh_token is not None
        user_repo.update.assert_called_once()  # last_login_at updated
        token_repo.create.assert_called_once()  # refresh token persisted

    @pytest.mark.asyncio
    async def test_login_wrong_email_raises(self):
        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = None
        token_repo = AsyncMock()

        use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
        dto = LoginRequest(email="wrong@example.com", password="StrongPass1")

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises(self):
        user = self._make_user()
        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = user
        token_repo = AsyncMock()

        use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
        dto = LoginRequest(email="test@example.com", password="WrongPass1")

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_social_only_account_raises(self):
        """User registered via OAuth (no password_hash)."""
        user = User(
            id=uuid4(),
            email="social@example.com",
            password_hash=None,
            display_name="Social User",
            username="socialuser",
        )
        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = user
        token_repo = AsyncMock()

        use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
        dto = LoginRequest(email="social@example.com", password="AnyPass1")

        with pytest.raises(InvalidCredentialsError, match="social login"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_updates_last_login(self):
        user = self._make_user()
        assert user.last_login_at is None

        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = user
        user_repo.update.return_value = user
        token_repo = AsyncMock()

        use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
        dto = LoginRequest(email="test@example.com", password="StrongPass1")
        await use_case.execute(dto)

        # User's last_login_at should be set
        update_call_user = user_repo.update.call_args[0][0]
        assert update_call_user.last_login_at is not None
        token_repo.create.assert_called_once()
