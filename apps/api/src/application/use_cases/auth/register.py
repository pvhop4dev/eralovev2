"""Register User Use Case.

Creates a new user account, hashes password, sends verification OTP.
"""

import secrets
from datetime import UTC, datetime
from uuid import uuid4

import structlog

from application.dtos.auth_dto import AuthResponse, RegisterRequest, UserResponse
from domain.entities.refresh_token import RefreshToken
from domain.entities.user import User
from domain.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.password import Password
from infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)

logger = structlog.get_logger()


class RegisterUserUseCase:
    """Register a new user.

    Flow:
    1. Validate email format and uniqueness
    2. Validate username uniqueness
    3. Hash password
    4. Create user in database
    5. Generate OTP and cache in Redis
    6. Send verification email
    7. Return user + tokens

    Raises:
        EmailAlreadyExistsError: If email is already registered.
        UsernameAlreadyExistsError: If username is already taken.
        ValidationError: If email or password format is invalid.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        redis_client: object,
        email_sender: object | None = None,
    ) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.redis = redis_client
        self.email_sender = email_sender

    async def execute(self, dto: RegisterRequest) -> tuple[AuthResponse, str]:
        """Execute the registration.

        Args:
            dto: Registration request data.

        Returns:
            Tuple of (AuthResponse, refresh_token).
        """
        # 1. Validate and normalize email
        email_vo = Email(dto.email)

        # 2. Check email uniqueness
        if await self.user_repo.email_exists(email_vo.value):
            raise EmailAlreadyExistsError()

        # 3. Check username uniqueness
        if await self.user_repo.username_exists(dto.username):
            raise UsernameAlreadyExistsError()

        # 4. Hash password
        password_vo = Password.from_plaintext(dto.password)

        # 5. Create user entity
        user = User(
            id=uuid4(),
            email=email_vo.value,
            password_hash=password_vo.hashed_value,
            display_name=dto.display_name,
            username=dto.username.lower(),
            date_of_birth=dto.date_of_birth,
            gender=dto.gender,
        )

        # 6. Persist user
        created_user = await self.user_repo.create(user)

        # 7. Generate OTP and cache in Redis (5 min TTL)
        otp = "".join(secrets.choice("0123456789") for _ in range(6))
        otp_key = f"eralove:otp:verify:{email_vo.value}"
        await self.redis.setex(otp_key, 300, otp)

        # 8. Send verification email (non-blocking)
        if self.email_sender:
            try:
                from infrastructure.email.email_service import send_verification_email
                await send_verification_email(email_vo.value, otp)
            except Exception as e:
                logger.warning("verification_email_failed", email=email_vo.value, error=str(e))

        # 9. Generate tokens
        access_token = create_access_token(created_user.id)
        refresh_token = create_refresh_token(created_user.id)

        # 9.1 Persist refresh token hash to DB
        payload = decode_token(refresh_token, expected_type="refresh")
        expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
        token_hash = hash_token(refresh_token)
        
        token_entity = RefreshToken(
            id=None,
            user_id=created_user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.token_repo.create(token_entity)

        logger.info("user_registered", user_id=str(created_user.id), email=email_vo.value)

        # 10. Build response
        user_response = UserResponse(
            id=str(created_user.id),
            email=created_user.email,
            display_name=created_user.display_name,
            username=created_user.username,
            avatar_url=created_user.avatar_url,
            date_of_birth=created_user.date_of_birth,
            gender=created_user.gender,
            zodiac_sign=created_user.zodiac_sign,
            is_email_verified=created_user.is_email_verified,
            is_onboarded=created_user.is_onboarded,
        )
        auth_response = AuthResponse(user=user_response, access_token=access_token)
        return auth_response, refresh_token
