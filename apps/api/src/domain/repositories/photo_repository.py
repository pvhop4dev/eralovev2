"""Photo Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.photo import Photo


class PhotoRepository(ABC):
    """Abstract repository for Photo persistence."""

    @abstractmethod
    async def create(self, photo: Photo) -> Photo:
        """Persist a new photo."""

    @abstractmethod
    async def get_by_id(self, photo_id: UUID) -> Photo | None:
        """Get photo by ID (excluding soft-deleted)."""

    @abstractmethod
    async def get_by_couple(
        self, couple_id: UUID, limit: int = 50, before_id: UUID | None = None
    ) -> list[Photo]:
        """Get photos for a couple (newest first, paginated)."""

    @abstractmethod
    async def get_by_event(self, event_id: UUID) -> list[Photo]:
        """Get all photos attached to a specific event."""

    @abstractmethod
    async def update(self, photo: Photo) -> Photo:
        """Update an existing photo's metadata."""

    @abstractmethod
    async def soft_delete(self, photo_id: UUID) -> None:
        """Soft delete a photo."""
