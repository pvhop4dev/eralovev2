"""Refresh Token Use Case.

Verifies the old refresh token, rotates the token pair, and persists the new token hash.
"""

from datetime import datetime, timezone
import structlog
from uuid import UUID

from domain.entities.refresh_token import RefreshToken
from domain.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository
from infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)

logger = structlog.get_logger()


class RefreshTokenUseCase:
    """Rotate Refresh Token and issue new Access Token.

    Flow:
    1. Decode and validate the provided refresh token
    2. Compute SHA256 hash of the token
    3. Check if hash exists in the repository
    4. If not, trigger replay attack protection (revoke all tokens for user)
    5. If expired in DB, delete it and raise error
    6. Verify user still exists
    7. Generate new Access Token + Refresh Token
    8. Delete the old refresh token from repository
    9. Persist the new refresh token hash
    10. Return the new tokens

    Raises:
        InvalidTokenError: Token is invalid, revoked, or used.
        TokenExpiredError: Token has expired.
        UserNotFoundError: User account no longer exists.
    """

    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(self, refresh_token: str) -> tuple[str, str]:
        """Execute token refresh and rotation.

        Args:
            refresh_token: The old refresh token string.

        Returns:
            Tuple of (new_access_token, new_refresh_token).
        """
        # 1. Decode refresh token (raises TokenExpiredError/InvalidTokenError if invalid)
        payload = decode_token(refresh_token, expected_type="refresh")
        
        try:
            user_id = UUID(payload["sub"])
        except (ValueError, KeyError):
            raise InvalidTokenError("Invalid user ID in token")

        # 2. Compute token hash
        old_hash = hash_token(refresh_token)

        # 3. Check if hash exists in DB
        token_entity = await self.token_repo.get_by_hash(old_hash)

        # 4. Replay attack detection
        if not token_entity:
            # Token is valid but not in DB -> indicates it has been used or revoked.
            # Revoke all tokens for this user for security.
            await self.token_repo.delete_all_for_user(user_id)
            logger.warning(
                "refresh_token_replay_detected",
                user_id=str(user_id),
                token_hash_prefix=old_hash[:8]
            )
            raise InvalidTokenError("Session has been revoked or refresh token reused")

        # 5. Check if expired in DB (double check)
        if token_entity.is_expired():
            await self.token_repo.delete_by_hash(old_hash)
            logger.warning(
                "refresh_token_expired_in_db",
                user_id=str(user_id),
                token_hash_prefix=old_hash[:8]
            )
            raise TokenExpiredError("Refresh token expired")

        # 6. Verify user still exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            # Clean up token if user no longer exists
            await self.token_repo.delete_by_hash(old_hash)
            raise UserNotFoundError()

        # 7. Generate new tokens
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        # 8. Delete old refresh token from DB
        await self.token_repo.delete_by_hash(old_hash)

        # 9. Persist the new refresh token hash
        new_payload = decode_token(new_refresh_token, expected_type="refresh")
        new_expires_at = datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc)
        new_token_hash = hash_token(new_refresh_token)

        new_token_entity = RefreshToken(
            id=None,
            user_id=user_id,
            token_hash=new_token_hash,
            expires_at=new_expires_at,
        )
        await self.token_repo.create(new_token_entity)

        logger.info(
            "refresh_token_rotated",
            user_id=str(user_id),
            old_hash_prefix=old_hash[:8],
            new_hash_prefix=new_token_hash[:8]
        )

        # 10. Return new tokens
        return new_access_token, new_refresh_token
