"""Decline Match Request Use Case."""

from uuid import UUID

import structlog

from domain.exceptions import ForbiddenError, NotFoundError
from domain.repositories.match_repository import MatchRequestRepository

logger = structlog.get_logger()


class DeclineMatchRequestUseCase:
    """Decline a match request."""

    def __init__(self, match_repo: MatchRequestRepository) -> None:
        self.match_repo = match_repo

    async def execute(self, user_id: UUID, request_id: UUID) -> None:
        match_request = await self.match_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundError("Match request not found")

        if match_request.receiver_id != user_id:
            raise ForbiddenError("Only the receiver can decline a match request")

        match_request.decline()
        await self.match_repo.update(match_request)

        logger.info("match_declined", request_id=str(request_id))
