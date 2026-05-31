"""Auth API Routes.

POST /api/v1/auth/register — Register new user
POST /api/v1/auth/login — Login with email/password
POST /api/v1/auth/refresh — Refresh access token
POST /api/v1/auth/logout — Logout (clear refresh cookie)
POST /api/v1/auth/verify-email — Verify email with OTP
POST /api/v1/auth/forgot-password — Send password reset email
"""

import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response

from application.dtos.auth_dto import (
    ForgotPasswordRequest,
    LoginRequest,
    OAuthLoginRequest,
    RegisterRequest,
    VerifyEmailRequest,
)
from application.use_cases.auth.login import LoginUserUseCase
from application.use_cases.auth.oauth_login import OAuthLoginUseCase
from application.use_cases.auth.refresh import RefreshTokenUseCase
from application.use_cases.auth.register import RegisterUserUseCase
from application.use_cases.auth.verify_email import VerifyEmailUseCase
from domain.exceptions import UnauthorizedError
from infrastructure.auth.jwt_handler import (
    hash_token,
)
from infrastructure.database.repositories.oauth_account_repository import (
    PostgresOAuthAccountRepository,
)
from infrastructure.database.repositories.refresh_token_repository import (
    PostgresRefreshTokenRepository,
)
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from infrastructure.email.email_service import send_reset_password_email
from presentation.deps import DbSession, RedisClient
from presentation.middleware.rate_limiter import RateLimiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cookie settings for refresh token
_REFRESH_COOKIE_NAME = "eralove_refresh_token"
_REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds

# Rate limiter for auth endpoints (10 requests per minute)
auth_limiter = RateLimiter(requests=10, window_seconds=60)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Set the refresh token as an httpOnly cookie."""
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=False,  # Set to True in production (requires HTTPS)
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh token cookie."""
    response.delete_cookie(
        key=_REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
    )


@router.post("/register", status_code=201, dependencies=[Depends(auth_limiter)])
async def register(
    body: RegisterRequest,
    response: Response,
    session: DbSession,
    redis: RedisClient,
) -> dict:
    """Register a new user account.

    Creates account, sends OTP verification email, returns JWT tokens.
    """
    user_repo = PostgresUserRepository(session)
    token_repo = PostgresRefreshTokenRepository(session)
    use_case = RegisterUserUseCase(
        user_repo=user_repo,
        token_repo=token_repo,
        redis_client=redis,
        email_sender=True,  # Enable email sending
    )
    auth_response, refresh_token = await use_case.execute(body)

    _set_refresh_cookie(response, refresh_token)

    return {
        "data": auth_response.model_dump(),
        "meta": None,
        "error": None,
    }


@router.post("/login", dependencies=[Depends(auth_limiter)])
async def login(
    body: LoginRequest,
    response: Response,
    session: DbSession,
) -> dict:
    """Login with email and password.

    Returns JWT access token and sets refresh token cookie.
    """
    user_repo = PostgresUserRepository(session)
    token_repo = PostgresRefreshTokenRepository(session)
    use_case = LoginUserUseCase(user_repo=user_repo, token_repo=token_repo)
    auth_response, refresh_token = await use_case.execute(body)

    _set_refresh_cookie(response, refresh_token)

    return {
        "data": auth_response.model_dump(),
        "meta": None,
        "error": None,
    }


@router.post("/oauth", dependencies=[Depends(auth_limiter)])
async def oauth_login(
    body: OAuthLoginRequest,
    response: Response,
    session: DbSession,
) -> dict:
    """Login or register with OAuth provider (Google)."""
    user_repo = PostgresUserRepository(session)
    oauth_repo = PostgresOAuthAccountRepository(session)
    token_repo = PostgresRefreshTokenRepository(session)

    use_case = OAuthLoginUseCase(
        user_repo=user_repo,
        oauth_repo=oauth_repo,
        token_repo=token_repo,
    )
    auth_response, refresh_token = await use_case.execute(body.provider, body.token)

    _set_refresh_cookie(response, refresh_token)

    return {
        "data": auth_response.model_dump(),
        "meta": None,
        "error": None,
    }


@router.post("/refresh")
async def refresh_token(
    response: Response,
    session: DbSession,
    eralove_refresh_token: Annotated[str | None, Cookie()] = None,
) -> dict:
    """Refresh the access token using the refresh token cookie.

    Rotates refresh token in cookie, returns a new access token.
    """
    if not eralove_refresh_token:
        raise UnauthorizedError("No refresh token provided")

    user_repo = PostgresUserRepository(session)
    token_repo = PostgresRefreshTokenRepository(session)
    use_case = RefreshTokenUseCase(user_repo=user_repo, token_repo=token_repo)

    # Rotate tokens (deletes old one, persists and returns new one)
    new_access_token, new_refresh_token = await use_case.execute(eralove_refresh_token)

    _set_refresh_cookie(response, new_refresh_token)

    return {
        "data": {"access_token": new_access_token},
        "meta": None,
        "error": None,
    }


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    session: DbSession,
    eralove_refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    """Logout — clear and revoke the refresh token."""
    if eralove_refresh_token:
        token_repo = PostgresRefreshTokenRepository(session)
        token_hash = hash_token(eralove_refresh_token)
        await token_repo.delete_by_hash(token_hash)

    _clear_refresh_cookie(response)


@router.post("/verify-email", dependencies=[Depends(auth_limiter)])
async def verify_email(
    body: VerifyEmailRequest,
    session: DbSession,
    redis: RedisClient,
) -> dict:
    """Verify email address with OTP code.

    The OTP was sent during registration via email.
    """
    user_repo = PostgresUserRepository(session)
    use_case = VerifyEmailUseCase(user_repo=user_repo, redis_client=redis)
    await use_case.execute(body)

    return {
        "data": {"verified": True},
        "meta": None,
        "error": None,
    }


@router.post("/forgot-password", dependencies=[Depends(auth_limiter)])
async def forgot_password(
    body: ForgotPasswordRequest,
    session: DbSession,
    redis: RedisClient,
) -> dict:
    """Send password reset email.

    Generates a reset token and sends it via email.
    Always returns success (to prevent email enumeration).
    """
    user_repo = PostgresUserRepository(session)
    user = await user_repo.get_by_email(body.email.lower())

    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_key = f"eralove:reset:{reset_token}"
        await redis.setex(reset_key, 900, str(user.id))  # 15 min TTL

        # Send email
        import contextlib
        with contextlib.suppress(Exception):
            await send_reset_password_email(user.email, reset_token)

    # Always return success to prevent email enumeration
    return {
        "data": {"message": "If the email exists, a reset link has been sent."},
        "meta": None,
        "error": None,
    }
