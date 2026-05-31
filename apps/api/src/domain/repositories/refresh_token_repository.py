"""Refresh Token Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(ABC):
    """Abstract interface for Refresh Token repository."""

    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshToken:
        """Persist a new refresh token."""
        pass

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve a refresh token by its SHA256 hash."""
        pass

    @abstractmethod
    async def delete_by_hash(self, token_hash: str) -> None:
        """Delete/revoke a specific refresh token by its hash."""
        pass

    @abstractmethod
    async def delete_all_for_user(self, user_id: UUID) -> None:
        """Delete/revoke all refresh tokens belonging to a user (force logout)."""
        pass
