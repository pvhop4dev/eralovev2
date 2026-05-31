"""OAuth Account Domain Entity."""

import uuid
from datetime import datetime


class OAuthAccount:
    """Domain representation of an OAuth connection (e.g., Google, Apple)."""

    def __init__(
        self,
        id: uuid.UUID | None,
        user_id: uuid.UUID,
        provider: str,
        provider_id: str,
        email: str | None = None,
        metadata: dict | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.provider = provider
        self.provider_id = provider_id
        self.email = email
        self.metadata = metadata or {}
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "provider": self.provider,
            "provider_id": self.provider_id,
            "email": self.email,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
