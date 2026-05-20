"""Auth DTOs (Data Transfer Objects).

Request/Response schemas for authentication endpoints.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: str = Field(..., max_length=255, description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    display_name: str = Field(..., min_length=1, max_length=100, description="Display name")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric + underscore)",
    )
    date_of_birth: date | None = Field(None, description="Date of birth")
    gender: str | None = Field(None, max_length=20, description="Gender")


class LoginRequest(BaseModel):
    """Request body for login."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class VerifyEmailRequest(BaseModel):
    """Request body for email verification."""

    email: str = Field(..., max_length=255)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password."""

    email: str = Field(..., max_length=255)


class ResetPasswordRequest(BaseModel):
    """Request body for password reset."""

    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    """User data in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    username: str
    avatar_url: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    zodiac_sign: str | None = None
    love_language: str | None = None
    bio: str | None = None
    is_email_verified: bool = False
    is_onboarded: bool = False


class AuthResponse(BaseModel):
    """Response after successful authentication."""

    user: UserResponse
    access_token: str


class TokenResponse(BaseModel):
    """Response for token refresh."""

    access_token: str


class UpdateUserRequest(BaseModel):
    """Request body for updating user profile."""

    display_name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=20)
