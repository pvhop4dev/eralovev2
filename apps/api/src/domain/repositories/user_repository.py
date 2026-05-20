"""User Repository Interface.

Abstract base class defining the contract for user data access.
Domain layer — no implementation details.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository for User entity persistence."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user.

        Args:
            user: User entity to persist.

        Returns:
            The created User with generated ID and timestamps.
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by their ID (excludes soft-deleted).

        Args:
            user_id: UUID of the user.

        Returns:
            User if found and not deleted, None otherwise.
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by their email (excludes soft-deleted).

        Args:
            email: Email address (case-insensitive).

        Returns:
            User if found, None otherwise.
        """
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Get a user by their username (excludes soft-deleted).

        Args:
            username: Username string.

        Returns:
            User if found, None otherwise.
        """
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User entity with updated fields.

        Returns:
            The updated User.
        """
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered.

        Args:
            email: Email address to check.

        Returns:
            True if email exists, False otherwise.
        """
        ...

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if a username is already taken.

        Args:
            username: Username to check.

        Returns:
            True if username exists, False otherwise.
        """
        ...

    @abstractmethod
    async def search(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> list[User]:
        """Search users by username or display_name.

        Args:
            query: Search query string.
            limit: Max results to return.
            offset: Results offset for pagination.

        Returns:
            List of matching users.
        """
        ...
