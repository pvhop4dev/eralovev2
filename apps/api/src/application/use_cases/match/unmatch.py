"""Unmatch Use Case."""

from uuid import UUID

import structlog

from domain.exceptions import CoupleNotFoundError
from domain.repositories.couple_repository import CoupleRepository

logger = structlog.get_logger()


class UnmatchUseCase:
    """Use case to unmatch the current active/paused couple relationship."""

    def __init__(self, couple_repo: CoupleRepository) -> None:
        self.couple_repo = couple_repo

    async def execute(self, user_id: UUID) -> None:
        """Execute unmatching/breaking up the relationship.

        Args:
            user_id: The ID of the user requesting the unmatch.

        Raises:
            CoupleNotFoundError: If the user is not in an active relationship.
        """
        couple = await self.couple_repo.get_active_for_user(user_id)
        if not couple:
            logger.warning("unmatch_failed_no_active_couple", user_id=str(user_id))
            raise CoupleNotFoundError()

        partner_id = couple.get_partner_id(user_id)
        logger.info(
            "unmatching_couple",
            couple_id=str(couple.id),
            user_id=str(user_id),
            partner_id=str(partner_id),
        )

        couple.break_up()
        await self.couple_repo.update(couple)

        logger.info(
            "couple_unmatched_successfully",
            couple_id=str(couple.id),
            user_id=str(user_id),
            partner_id=str(partner_id),
        )
