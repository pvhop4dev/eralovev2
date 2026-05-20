"""Couple Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.couple import Couple


class CoupleRepository(ABC):
    """Abstract repository for Couple persistence."""

    @abstractmethod
    async def create(self, couple: Couple) -> Couple:
        """Persist a new couple."""

    @abstractmethod
    async def get_by_id(self, couple_id: UUID) -> Couple | None:
        """Get couple by ID."""

    @abstractmethod
    async def get_active_for_user(self, user_id: UUID) -> Couple | None:
        """Get the active couple for a user (at most one)."""

    @abstractmethod
    async def update(self, couple: Couple) -> Couple:
        """Update an existing couple."""
