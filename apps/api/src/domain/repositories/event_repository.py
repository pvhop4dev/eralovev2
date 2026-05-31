"""LoveEvent Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.love_event import LoveEvent


class LoveEventRepository(ABC):
    """Abstract repository for LoveEvent persistence."""

    @abstractmethod
    async def create(self, event: LoveEvent) -> LoveEvent:
        """Persist a new event."""

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> LoveEvent | None:
        """Get event by ID (excluding soft-deleted)."""

    @abstractmethod
    async def get_by_couple_and_month(
        self, couple_id: UUID, year: int, month: int
    ) -> list[LoveEvent]:
        """Get all events for a couple in a given month."""

    @abstractmethod
    async def get_upcoming(self, couple_id: UUID, days: int = 7) -> list[LoveEvent]:
        """Get upcoming events within N days."""

    @abstractmethod
    async def update(self, event: LoveEvent) -> LoveEvent:
        """Update an existing event."""

    @abstractmethod
    async def soft_delete(self, event_id: UUID) -> None:
        """Soft delete an event."""

    @abstractmethod
    async def get_past_events_on_this_day(self, couple_id: UUID) -> list[LoveEvent]:
        """Get all past events for a couple that happened on this day in previous years."""

