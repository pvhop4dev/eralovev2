"""Verify Email Use Case.

Verifies a user's email using the OTP code sent during registration.
"""

import structlog

from application.dtos.auth_dto import VerifyEmailRequest
from domain.exceptions import UserNotFoundError, ValidationError
from domain.repositories.user_repository import UserRepository

logger = structlog.get_logger()


class VerifyEmailUseCase:
    """Verify user's email with OTP.

    Flow:
    1. Check OTP in Redis cache
    2. Mark user.is_email_verified = True
    3. Delete OTP from Redis

    Raises:
        ValidationError: If OTP is invalid or expired.
        UserNotFoundError: If user not found.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        redis_client: object,
    ) -> None:
        self.user_repo = user_repo
        self.redis = redis_client

    async def execute(self, dto: VerifyEmailRequest) -> bool:
        """Execute email verification.

        Args:
            dto: Verification request with email and OTP.

        Returns:
            True if verification succeeded.
        """
        email = dto.email.lower()
        otp_key = f"eralove:otp:verify:{email}"

        # 1. Check OTP
        stored_otp = await self.redis.get(otp_key)
        if not stored_otp:
            raise ValidationError("OTP has expired. Please request a new one.")

        if stored_otp != dto.otp:
            raise ValidationError("Invalid OTP code.")

        # 2. Find and update user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundError()

        user.verify_email()
        await self.user_repo.update(user)

        # 3. Delete OTP from Redis
        await self.redis.delete(otp_key)

        logger.info("email_verified", user_id=str(user.id), email=email)
        return True
