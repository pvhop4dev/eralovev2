"""OAuth Account Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.oauth_account import OAuthAccount


class OAuthAccountRepository(ABC):
    """Abstract interface for OAuth Account repository."""

    @abstractmethod
    async def create(self, oauth_account: OAuthAccount) -> OAuthAccount:
        """Persist a new OAuth account connection."""
        pass

    @abstractmethod
    async def get_by_provider(self, provider: str, provider_id: str) -> OAuthAccount | None:
        """Retrieve an OAuth account by provider name and provider's user ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[OAuthAccount]:
        """Retrieve all OAuth connections for a user."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete/unlink an OAuth account connection."""
        pass
