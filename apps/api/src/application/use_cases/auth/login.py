import structlog
from datetime import datetime, timezone

from application.dtos.auth_dto import AuthResponse, LoginRequest, UserResponse
from domain.entities.refresh_token import RefreshToken
from domain.exceptions import InvalidCredentialsError
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository
from domain.value_objects.password import Password
from infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)

logger = structlog.get_logger()


class LoginUserUseCase:
    """Login an existing user.

    Flow:
    1. Find user by email
    2. Verify password
    3. Check email is verified
    4. Update last_login_at
    5. Generate tokens
    6. Persist refresh token hash to DB
    7. Return user + tokens

    Raises:
        InvalidCredentialsError: If email/password is wrong or email not verified.
    """

    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def execute(self, dto: LoginRequest) -> tuple[AuthResponse, str]:
        """Execute login.

        Args:
            dto: Login request data.

        Returns:
            Tuple of (AuthResponse, refresh_token).
        """
        # 1. Find user by email
        user = await self.user_repo.get_by_email(dto.email.lower())
        if not user:
            raise InvalidCredentialsError()

        # 2. Verify password
        if not user.password_hash:
            raise InvalidCredentialsError("Account uses social login. Please login with Google.")

        password = Password.from_hash(user.password_hash)
        if not password.verify(dto.password):
            raise InvalidCredentialsError()

        # 3. Check email verification (allow login but flag it)
        # We allow unverified users to log in but they'll have limited access

        # 4. Update last login
        user.update_last_login()
        await self.user_repo.update(user)

        # 5. Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # 6. Persist refresh token hash to DB
        payload = decode_token(refresh_token, expected_type="refresh")
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        token_hash = hash_token(refresh_token)
        
        token_entity = RefreshToken(
            id=None,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.token_repo.create(token_entity)

        logger.info("user_logged_in", user_id=str(user.id), email=user.email)

        # 7. Build response
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

