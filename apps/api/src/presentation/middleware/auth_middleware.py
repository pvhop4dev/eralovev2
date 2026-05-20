"""Auth Middleware — JWT Authentication Dependency.

Extracts and validates JWT token from Authorization header.
Provides CurrentUser dependency for protected routes.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.entities.user import User
from domain.exceptions import UnauthorizedError, UserNotFoundError
from domain.repositories.user_repository import UserRepository
from infrastructure.auth.jwt_handler import get_user_id_from_token
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from presentation.deps import DbSession

# HTTP Bearer scheme — extracts token from "Authorization: Bearer <token>"
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ] = None,
) -> User:
    """Extract and validate the current user from JWT.

    Usage in route:
        current_user: CurrentUser

    Raises:
        UnauthorizedError: If no token or invalid token.
        UserNotFoundError: If user no longer exists.
    """
    if not credentials:
        raise UnauthorizedError("Authentication required. Please provide a Bearer token.")

    # Decode JWT → get user_id
    user_id = get_user_id_from_token(credentials.credentials, expected_type="access")

    # Fetch user from database
    user_repo = PostgresUserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError("User account not found or has been deleted")

    return user


# Type alias for clean route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
