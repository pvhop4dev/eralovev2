"""OAuth Login Use Case.

Handles authentication with third-party providers (Google).
"""

from datetime import UTC, datetime

import httpx
import structlog

from application.dtos.auth_dto import AuthResponse, UserResponse
from domain.entities.oauth_account import OAuthAccount
from domain.entities.refresh_token import RefreshToken
from domain.entities.user import User
from domain.exceptions import InvalidTokenError
from domain.repositories.oauth_account_repository import OAuthAccountRepository
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository
from infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)

logger = structlog.get_logger()


class OAuthLoginUseCase:
    """Login or register a user using an OAuth provider (e.g. Google).

    Flow:
    1. Verify token with OAuth provider's Token Info API
    2. Check if an OAuthAccount connection already exists
    3. If yes, fetch the linked User
    4. If no, check if a User exists with the provider's verified email
       - If user exists: link new OAuthAccount to user
       - If user does not exist: create new User with verified email + link OAuthAccount
    5. Update user's last_login_at
    6. Generate Access Token + Refresh Token
    7. Persist Refresh Token hash to DB
    8. Return user + tokens

    Raises:
        InvalidTokenError: If token is invalid or missing required claims.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        oauth_repo: OAuthAccountRepository,
        token_repo: RefreshTokenRepository,
    ) -> None:
        self.user_repo = user_repo
        self.oauth_repo = oauth_repo
        self.token_repo = token_repo

    async def execute(self, provider: str, token: str) -> tuple[AuthResponse, str]:
        """Execute the OAuth login flow.

        Args:
            provider: The OAuth provider name (must be 'google').
            token: The credential token (Google ID token).

        Returns:
            Tuple of (AuthResponse, refresh_token).
        """
        if provider.lower() != "google":
            raise InvalidTokenError(f"Unsupported OAuth provider: {provider}")

        # 1. Verify token with Google
        payload = await self._verify_google_token(token)
        provider_id = payload.get("sub")
        email = payload.get("email")
        display_name = payload.get("name", "Eralove User")
        avatar_url = payload.get("picture")

        if not provider_id or not email:
            raise InvalidTokenError("OAuth token missing required fields (sub, email)")

        # 2. Check if OAuth link exists
        oauth_account = await self.oauth_repo.get_by_provider(provider, provider_id)
        user = None

        if oauth_account:
            # Get existing user
            user = await self.user_repo.get_by_id(oauth_account.user_id)
            if not user:
                # Clean up dangling link
                await self.oauth_repo.delete(oauth_account.id)
                oauth_account = None

        if not oauth_account:
            # 3. Check if user already exists with this email
            user = await self.user_repo.get_by_email(email.lower())

            if not user:
                # 4. Register new user
                # Extract username from email and ensure it is unique
                base_username = email.split("@")[0]
                username = base_username.lower()

                counter = 1
                while await self.user_repo.username_exists(username):
                    username = f"{base_username}{counter}".lower()
                    counter += 1

                user = User(
                    id=None,
                    email=email.lower(),
                    password_hash=None,  # social only
                    display_name=display_name,
                    username=username,
                    avatar_url=avatar_url,
                    is_email_verified=True,
                    is_onboarded=False,
                )
                user = await self.user_repo.create(user)
                logger.info("oauth_user_created", user_id=str(user.id), email=email)

            # 5. Link OAuth Account
            oauth_account = OAuthAccount(
                id=None,
                user_id=user.id,
                provider=provider,
                provider_id=provider_id,
                email=email.lower(),
                metadata=payload,
            )
            await self.oauth_repo.create(oauth_account)
            logger.info("oauth_account_linked", user_id=str(user.id), provider=provider)

        # 6. Update last login
        user.update_last_login()
        await self.user_repo.update(user)

        # 7. Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # 8. Persist refresh token hash
        refresh_payload = decode_token(refresh_token, expected_type="refresh")
        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=UTC)
        token_hash = hash_token(refresh_token)

        token_entity = RefreshToken(
            id=None,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.token_repo.create(token_entity)

        logger.info("oauth_user_logged_in", user_id=str(user.id), email=user.email)

        # 9. Build response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            username=user.username,
            avatar_url=user.avatar_url,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            zodiac_sign=user.zodiac_sign,
            love_language=user.love_language,
            bio=user.bio,
            is_email_verified=user.is_email_verified,
            is_onboarded=user.is_onboarded,
        )
        auth_response = AuthResponse(user=user_response, access_token=access_token)
        return auth_response, refresh_token

    async def _verify_google_token(self, token: str) -> dict:
        """Verify token with Google's tokeninfo endpoint."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": token},
                    timeout=5.0,
                )
            except httpx.RequestError as e:
                logger.error("oauth_google_verify_failed", error=str(e))
                raise InvalidTokenError("Failed to connect to Google OAuth service") from e

            if response.status_code != 200:
                raise InvalidTokenError("Invalid Google ID token")
            return response.json()
