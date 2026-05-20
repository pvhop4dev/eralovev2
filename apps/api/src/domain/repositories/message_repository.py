"""Message Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.message import Message


class MessageRepository(ABC):
    """Abstract repository for Message persistence."""

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """Persist a new message."""

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Get message by ID."""

    @abstractmethod
    async def get_by_couple(
        self, couple_id: UUID, limit: int = 50, before_id: UUID | None = None
    ) -> list[Message]:
        """Get messages for a couple (paginated, newest first)."""

    @abstractmethod
    async def get_pinned(self, couple_id: UUID) -> list[Message]:
        """Get pinned messages for a couple."""

    @abstractmethod
    async def update(self, message: Message) -> Message:
        """Update an existing message."""

    @abstractmethod
    async def mark_read_for_user(self, couple_id: UUID, reader_id: UUID) -> int:
        """Mark all unread messages as read for a user. Returns count."""
