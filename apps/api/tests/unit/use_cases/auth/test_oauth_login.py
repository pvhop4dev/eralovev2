"""Tests for OAuth Login Use Case."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from application.use_cases.auth.oauth_login import OAuthLoginUseCase
from domain.entities.oauth_account import OAuthAccount
from domain.entities.user import User
from domain.exceptions import InvalidTokenError


class TestOAuthLoginUseCase:
    """Test suite for OAuthLoginUseCase."""

    def _make_user(self) -> User:
        return User(
            id=uuid4(),
            email="test@example.com",
            password_hash=None,
            display_name="Test User",
            username="testuser",
            avatar_url="https://example.com/avatar.jpg",
            is_email_verified=True,
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_oauth_login_success_existing_link(self, mock_get):
        """Test login success when OAuth account and user already exist."""
        # Mock Google Token Info Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "google_id_123",
            "email": "test@example.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_get.return_value = mock_response

        # Mock Repositories
        user = self._make_user()
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        user_repo.update.return_value = user

        oauth_account = OAuthAccount(
            id=uuid4(),
            user_id=user.id,
            provider="google",
            provider_id="google_id_123",
            email="test@example.com",
        )
        oauth_repo = AsyncMock()
        oauth_repo.get_by_provider.return_value = oauth_account

        token_repo = AsyncMock()

        use_case = OAuthLoginUseCase(
            user_repo=user_repo, oauth_repo=oauth_repo, token_repo=token_repo
        )

        auth_response, refresh_token = await use_case.execute("google", "valid_google_token")

        assert auth_response.user.email == "test@example.com"
        assert auth_response.user.display_name == "Test User"
        assert auth_response.access_token is not None
        assert refresh_token is not None

        # Verify calls
        oauth_repo.get_by_provider.assert_called_once_with("google", "google_id_123")
        user_repo.get_by_id.assert_called_once_with(user.id)
        user_repo.update.assert_called_once()
        token_repo.create.assert_called_once()
        oauth_repo.create.assert_not_called()  # already linked

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_oauth_login_auto_link_existing_email(self, mock_get):
        """Test auto-linking when user with email exists but OAuth account doesn't."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "google_id_123",
            "email": "test@example.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.jpg",
        }
        mock_get.return_value = mock_response

        user = self._make_user()
        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = user
        user_repo.update.return_value = user

        oauth_repo = AsyncMock()
        oauth_repo.get_by_provider.return_value = None  # No link yet
        oauth_repo.create.return_value = MagicMock()

        token_repo = AsyncMock()

        use_case = OAuthLoginUseCase(
            user_repo=user_repo, oauth_repo=oauth_repo, token_repo=token_repo
        )

        auth_response, refresh_token = await use_case.execute("google", "valid_google_token")

        assert auth_response.user.email == "test@example.com"
        assert auth_response.access_token is not None

        # Verify OAuth Account created and linked
        oauth_repo.get_by_provider.assert_called_once_with("google", "google_id_123")
        user_repo.get_by_email.assert_called_once_with("test@example.com")
        oauth_repo.create.assert_called_once()  # New link created
        # Linked to existing user ID
        linked_oauth = oauth_repo.create.call_args[0][0]
        assert linked_oauth.user_id == user.id
        assert linked_oauth.provider == "google"
        assert linked_oauth.provider_id == "google_id_123"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_oauth_login_register_new_user(self, mock_get):
        """Test auto-registering new user and linking OAuth account."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "google_id_123",
            "email": "newuser@example.com",
            "name": "New Google User",
            "picture": "https://example.com/new_avatar.jpg",
        }
        mock_get.return_value = mock_response

        user_repo = AsyncMock()
        user_repo.get_by_email.return_value = None  # No user exists
        user_repo.username_exists.return_value = False  # 'newuser' username available

        # Mock user creation
        new_user = User(
            id=uuid4(),
            email="newuser@example.com",
            password_hash=None,
            display_name="New Google User",
            username="newuser",
            avatar_url="https://example.com/new_avatar.jpg",
            is_email_verified=True,
        )
        user_repo.create.return_value = new_user
        user_repo.update.return_value = new_user

        oauth_repo = AsyncMock()
        oauth_repo.get_by_provider.return_value = None
        oauth_repo.create.return_value = MagicMock()

        token_repo = AsyncMock()

        use_case = OAuthLoginUseCase(
            user_repo=user_repo, oauth_repo=oauth_repo, token_repo=token_repo
        )

        auth_response, refresh_token = await use_case.execute("google", "valid_google_token")

        assert auth_response.user.email == "newuser@example.com"
        assert auth_response.user.username == "newuser"
        assert auth_response.user.avatar_url == "https://example.com/new_avatar.jpg"
        assert auth_response.access_token is not None

        # Verify user created and linked
        user_repo.create.assert_called_once()
        oauth_repo.create.assert_called_once()

        created_user = user_repo.create.call_args[0][0]
        assert created_user.email == "newuser@example.com"
        assert created_user.username == "newuser"
        assert created_user.password_hash is None
        assert created_user.is_email_verified is True

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_oauth_login_invalid_token_raises(self, mock_get):
        """Test failure when Google Token Info returns error status."""
        mock_response = MagicMock()
        mock_response.status_code = 400  # Invalid token
        mock_get.return_value = mock_response

        user_repo = AsyncMock()
        oauth_repo = AsyncMock()
        token_repo = AsyncMock()

        use_case = OAuthLoginUseCase(
            user_repo=user_repo, oauth_repo=oauth_repo, token_repo=token_repo
        )

        with pytest.raises(InvalidTokenError, match="Invalid Google ID token"):
            await use_case.execute("google", "bad_google_token")

        user_repo.create.assert_not_called()
        oauth_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_oauth_login_invalid_provider_raises(self):
        """Test failure when provider is not supported."""
        user_repo = AsyncMock()
        oauth_repo = AsyncMock()
        token_repo = AsyncMock()

        use_case = OAuthLoginUseCase(
            user_repo=user_repo, oauth_repo=oauth_repo, token_repo=token_repo
        )

        with pytest.raises(InvalidTokenError, match="Unsupported OAuth provider"):
            await use_case.execute("apple", "token")
