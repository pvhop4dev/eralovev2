"""JWT Token Handler.

Creates and decodes JWT access tokens and refresh tokens.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt

from domain.exceptions import InvalidTokenError, TokenExpiredError
from infrastructure.config import get_settings

settings = get_settings()


def create_access_token(user_id: UUID) -> str:
    """Create a short-lived JWT access token.

    Args:
        user_id: UUID of the authenticated user.

    Returns:
        Encoded JWT string (exp: 15 minutes by default).
    """
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expires,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a long-lived JWT refresh token.

    Args:
        user_id: UUID of the authenticated user.

    Returns:
        Encoded JWT string (exp: 7 days by default).
    """
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expires,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.
        expected_type: Expected token type ("access" or "refresh").

    Returns:
        Token payload dict with "sub" (user_id) and "exp".

    Raises:
        TokenExpiredError: Token has expired.
        InvalidTokenError: Token is invalid or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError:
        raise InvalidTokenError("Invalid token")

    # Validate token type
    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"Expected {expected_type} token, got {payload.get('type')}")

    # Validate subject exists
    if not payload.get("sub"):
        raise InvalidTokenError("Token missing subject")

    return payload


def get_user_id_from_token(token: str, expected_type: str = "access") -> UUID:
    """Extract user_id (UUID) from a JWT token.

    Args:
        token: Encoded JWT string.
        expected_type: Expected token type.

    Returns:
        User UUID from the token's "sub" claim.
    """
    payload = decode_token(token, expected_type)
    try:
        return UUID(payload["sub"])
    except (ValueError, KeyError):
        raise InvalidTokenError("Invalid user ID in token")
