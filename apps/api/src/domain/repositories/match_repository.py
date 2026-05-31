"""Match Request Repository Interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.match_request import MatchRequest


class MatchRequestRepository(ABC):
    """Abstract repository for MatchRequest persistence."""

    @abstractmethod
    async def create(self, match_request: MatchRequest) -> MatchRequest:
        """Persist a new match request."""

    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> MatchRequest | None:
        """Get match request by ID."""

    @abstractmethod
    async def get_pending_for_user(self, user_id: UUID) -> list[MatchRequest]:
        """Get pending requests where user is receiver."""

    @abstractmethod
    async def get_sent_by_user(self, user_id: UUID) -> list[MatchRequest]:
        """Get requests sent by user."""

    @abstractmethod
    async def get_pending_between(self, sender_id: UUID, receiver_id: UUID) -> MatchRequest | None:
        """Get pending request between two specific users."""

    @abstractmethod
    async def update(self, match_request: MatchRequest) -> MatchRequest:
        """Update an existing match request."""
