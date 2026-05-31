"""Refresh Token Domain Entity."""

import uuid
from datetime import UTC, datetime


class RefreshToken:
    """Domain representation of a Refresh Token."""

    def __init__(
        self,
        id: uuid.UUID | None,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        created_at: datetime | None = None,
        device_info: dict | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.created_at = created_at
        self.device_info = device_info

    def is_expired(self) -> bool:
        """Check if this token has expired."""
        # Convert expires_at to timezone-aware UTC if it is naive
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)

        now = datetime.now(UTC)
        return now > exp

    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_hash": self.token_hash,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "device_info": self.device_info,
        }
