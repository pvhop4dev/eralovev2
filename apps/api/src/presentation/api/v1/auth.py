"""Auth API Routes.

POST /api/v1/auth/register — Register new user
POST /api/v1/auth/login — Login with email/password
POST /api/v1/auth/refresh — Refresh access token
POST /api/v1/auth/logout — Logout (clear refresh cookie)
POST /api/v1/auth/verify-email — Verify email with OTP
POST /api/v1/auth/forgot-password — Send password reset email
"""

import secrets

from fastapi import APIRouter, Response, Cookie
from typing import Annotated

from application.dtos.auth_dto import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from application.use_cases.auth.login import LoginUserUseCase
from application.use_cases.auth.register import RegisterUserUseCase
from application.use_cases.auth.verify_email import VerifyEmailUseCase
from domain.exceptions import UnauthorizedError, UserNotFoundError, ValidationError
from infrastructure.auth.jwt_handler import (
    create_access_token,
    get_user_id_from_token,
)
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from infrastructure.email.email_service import send_reset_password_email
from presentation.deps import DbSession, RedisClient

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cookie settings for refresh token
_REFRESH_COOKIE_NAME = "eralove_refresh_token"
_REFRESH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


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


@router.post("/register", status_code=201)
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
    use_case = RegisterUserUseCase(
        user_repo=user_repo,
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


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    session: DbSession,
) -> dict:
    """Login with email and password.

    Returns JWT access token and sets refresh token cookie.
    """
    user_repo = PostgresUserRepository(session)
    use_case = LoginUserUseCase(user_repo=user_repo)
    auth_response, refresh_token = await use_case.execute(body)

    _set_refresh_cookie(response, refresh_token)

    return {
        "data": auth_response.model_dump(),
        "meta": None,
        "error": None,
    }


@router.post("/refresh")
async def refresh_token(
    session: DbSession,
    eralove_refresh_token: Annotated[str | None, Cookie()] = None,
) -> dict:
    """Refresh the access token using the refresh token cookie.

    Returns a new access token. Requires valid refresh token in cookie.
    """
    if not eralove_refresh_token:
        raise UnauthorizedError("No refresh token provided")

    # Decode refresh token
    user_id = get_user_id_from_token(eralove_refresh_token, expected_type="refresh")

    # Verify user still exists
    user_repo = PostgresUserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError("User account not found")

    # Issue new access token
    new_access_token = create_access_token(user.id)

    return {
        "data": {"access_token": new_access_token},
        "meta": None,
        "error": None,
    }


@router.post("/logout", status_code=204)
async def logout(response: Response) -> None:
    """Logout — clear the refresh token cookie."""
    _clear_refresh_cookie(response)


@router.post("/verify-email")
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


@router.post("/forgot-password")
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
        try:
            await send_reset_password_email(user.email, reset_token)
        except Exception:
            pass  # Don't fail the request

    # Always return success to prevent email enumeration
    return {
        "data": {"message": "If the email exists, a reset link has been sent."},
        "meta": None,
        "error": None,
    }
