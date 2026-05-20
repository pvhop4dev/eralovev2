"""Send Match Request Use Case."""

from uuid import UUID, uuid4

import structlog

from application.dtos.match_dto import MatchRequestResponse, SendMatchRequestDTO
from domain.entities.match_request import MatchRequest
from domain.exceptions import (
    AlreadyMatchedError,
    BusinessRuleError,
    ConflictError,
    UserNotFoundError,
)
from domain.repositories.couple_repository import CoupleRepository
from domain.repositories.match_repository import MatchRequestRepository
from domain.repositories.user_repository import UserRepository

logger = structlog.get_logger()


class SendMatchRequestUseCase:
    """Send a match request to another user.

    Rules:
    - Cannot send to yourself
    - Cannot send if already matched with someone
    - Cannot send if receiver already matched
    - Cannot send duplicate pending request
    """

    def __init__(
        self,
        user_repo: UserRepository,
        match_repo: MatchRequestRepository,
        couple_repo: CoupleRepository,
    ) -> None:
        self.user_repo = user_repo
        self.match_repo = match_repo
        self.couple_repo = couple_repo

    async def execute(
        self, sender_id: UUID, dto: SendMatchRequestDTO
    ) -> MatchRequestResponse:
        receiver_id = UUID(dto.receiver_id)

        # 1. No self-match
        if sender_id == receiver_id:
            raise BusinessRuleError("You cannot send a match request to yourself")

        # 2. Check receiver exists
        receiver = await self.user_repo.get_by_id(receiver_id)
        if not receiver:
            raise UserNotFoundError("User not found")

        # 3. Check sender not already matched
        sender_couple = await self.couple_repo.get_active_for_user(sender_id)
        if sender_couple:
            raise AlreadyMatchedError()

        # 4. Check receiver not already matched
        receiver_couple = await self.couple_repo.get_active_for_user(receiver_id)
        if receiver_couple:
            raise BusinessRuleError("This user is already matched with someone")

        # 5. Check no duplicate pending request
        existing = await self.match_repo.get_pending_between(sender_id, receiver_id)
        if existing:
            raise ConflictError("You already have a pending request to this user")

        # Also check reverse direction
        reverse = await self.match_repo.get_pending_between(receiver_id, sender_id)
        if reverse:
            raise ConflictError("This user has already sent you a match request. Check your inbox!")

        # 6. Create match request
        match_request = MatchRequest(
            id=uuid4(),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=dto.message,
            proposed_start_date=dto.proposed_start_date,
        )
        created = await self.match_repo.create(match_request)

        logger.info("match_request_sent", sender=str(sender_id), receiver=str(receiver_id))

        sender = await self.user_repo.get_by_id(sender_id)
        return MatchRequestResponse(
            id=str(created.id),
            sender_id=str(created.sender_id),
            receiver_id=str(created.receiver_id),
            message=created.message,
            status=created.status,
            proposed_start_date=created.proposed_start_date,
            expires_at=created.expires_at.isoformat() if created.expires_at else None,
            created_at=created.created_at.isoformat() if created.created_at else None,
            sender_name=sender.display_name if sender else None,
            sender_username=sender.username if sender else None,
            receiver_name=receiver.display_name,
            receiver_username=receiver.username,
        )
