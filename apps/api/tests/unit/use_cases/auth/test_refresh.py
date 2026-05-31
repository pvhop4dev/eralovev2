"""Tests for Refresh Token Use Case."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.use_cases.auth.refresh import RefreshTokenUseCase
from domain.entities.refresh_token import RefreshToken
from domain.entities.user import User
from domain.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from infrastructure.auth.jwt_handler import create_refresh_token, hash_token


class TestRefreshTokenUseCase:
    """Test suite for RefreshTokenUseCase."""

    def _make_user(self) -> User:
        return User(
            id=uuid4(),
            email="test@example.com",
            password_hash="$2b$12$fakehash",
            display_name="Test User",
            username="testuser",
        )

    def _make_token_entity(self, user_id, token_hash, expired=False) -> RefreshToken:
        if expired:
            expires_at = datetime.now(UTC) - timedelta(days=1)
        else:
            expires_at = datetime.now(UTC) + timedelta(days=7)

        return RefreshToken(
            id=uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

    @pytest.mark.asyncio
    async def test_refresh_success(self):
        import asyncio

        user = self._make_user()
        old_refresh_token = create_refresh_token(user.id)
        old_hash = hash_token(old_refresh_token)

        token_entity = self._make_token_entity(user.id, old_hash, expired=False)

        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user

        token_repo = AsyncMock()
        token_repo.get_by_hash.return_value = token_entity

        # Sleep to ensure expiration timestamp increases by at least 1 second
        await asyncio.sleep(1.1)

        use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)
        new_access, new_refresh = await use_case.execute(old_refresh_token)

        assert new_access is not None
        assert new_refresh is not None
        assert new_refresh != old_refresh_token

        token_repo.get_by_hash.assert_called_once_with(old_hash)
        token_repo.delete_by_hash.assert_called_once_with(old_hash)
        token_repo.create.assert_called_once()
        user_repo.get_by_id.assert_called_once_with(user.id)

    @pytest.mark.asyncio
    async def test_refresh_replay_attack_revokes_all(self):
        """Token is valid signature wise but hash is not in DB."""
        user_id = uuid4()
        old_refresh_token = create_refresh_token(user_id)

        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_repo.get_by_hash.return_value = None  # Not found in DB

        use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)

        with pytest.raises(InvalidTokenError, match="Session has been revoked"):
            await use_case.execute(old_refresh_token)

        # Replay attack action: revoke all sessions of this user
        token_repo.delete_all_for_user.assert_called_once_with(user_id)
        token_repo.delete_by_hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_expired_token_raises(self):
        user = self._make_user()
        old_refresh_token = create_refresh_token(user.id)
        old_hash = hash_token(old_refresh_token)

        # Expired token record
        token_entity = self._make_token_entity(user.id, old_hash, expired=True)

        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_repo.get_by_hash.return_value = token_entity

        use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)

        with pytest.raises(TokenExpiredError):
            await use_case.execute(old_refresh_token)

        # Expired token must be cleaned up from database
        token_repo.delete_by_hash.assert_called_once_with(old_hash)
        token_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_invalid_signature_raises(self):
        user_repo = AsyncMock()
        token_repo = AsyncMock()

        use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)

        with pytest.raises(InvalidTokenError, match="Invalid token"):
            await use_case.execute("invalid.token.string")

        token_repo.get_by_hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_user_not_found_raises(self):
        user_id = uuid4()
        old_refresh_token = create_refresh_token(user_id)
        old_hash = hash_token(old_refresh_token)

        token_entity = self._make_token_entity(user_id, old_hash, expired=False)

        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = None  # User no longer exists

        token_repo = AsyncMock()
        token_repo.get_by_hash.return_value = token_entity

        use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(old_refresh_token)

        # Expired token cleanup
        token_repo.delete_by_hash.assert_called_once_with(old_hash)
        token_repo.create.assert_not_called()
