"""Accept Match Request Use Case."""

from datetime import date
from uuid import UUID, uuid4

import structlog

from application.dtos.match_dto import AcceptMatchRequestDTO, CoupleResponse
from domain.entities.couple import Couple
from domain.exceptions import ForbiddenError, NotFoundError
from domain.repositories.couple_repository import CoupleRepository
from domain.repositories.match_repository import MatchRequestRepository

logger = structlog.get_logger()


class AcceptMatchRequestUseCase:
    """Accept a match request and create a couple.

    Rules:
    - Only the receiver can accept
    - Must be pending and not expired
    - Creates a Couple record
    """

    def __init__(
        self,
        match_repo: MatchRequestRepository,
        couple_repo: CoupleRepository,
    ) -> None:
        self.match_repo = match_repo
        self.couple_repo = couple_repo

    async def execute(
        self, user_id: UUID, request_id: UUID, dto: AcceptMatchRequestDTO
    ) -> CoupleResponse:
        # 1. Get match request
        match_request = await self.match_repo.get_by_id(request_id)
        if not match_request:
            raise NotFoundError("Match request not found")

        # 2. Verify the current user is the receiver
        if match_request.receiver_id != user_id:
            raise ForbiddenError("Only the receiver can accept a match request")

        # 3. Accept (validates pending + not expired)
        match_request.accept(start_date=dto.start_date)
        await self.match_repo.update(match_request)

        # 4. Create couple
        couple = Couple(
            id=uuid4(),
            user1_id=match_request.sender_id,
            user2_id=match_request.receiver_id,
            start_date=dto.start_date or date.today(),
        )
        created_couple = await self.couple_repo.create(couple)

        logger.info(
            "match_accepted",
            couple_id=str(created_couple.id),
            user1=str(match_request.sender_id),
            user2=str(match_request.receiver_id),
        )

        return CoupleResponse(
            id=str(created_couple.id),
            user1_id=str(created_couple.user1_id),
            user2_id=str(created_couple.user2_id),
            start_date=created_couple.start_date,
            status=created_couple.status,
            theme_color=created_couple.theme_color,
            days_together=created_couple.days_together,
        )
