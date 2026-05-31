"""PostgreSQL Match Request Repository Implementation."""

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.match_request import MatchRequest
from domain.repositories.match_repository import MatchRequestRepository
from infrastructure.database.models.match_request_model import MatchRequestModel


class PostgresMatchRequestRepository(MatchRequestRepository):
    """PostgreSQL-backed match request repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, match_request: MatchRequest) -> MatchRequest:
        model = MatchRequestModel(
            id=match_request.id,
            sender_id=match_request.sender_id,
            receiver_id=match_request.receiver_id,
            message=match_request.message,
            status=match_request.status,
            proposed_start_date=match_request.proposed_start_date,
            expires_at=match_request.expires_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, request_id: UUID) -> MatchRequest | None:
        stmt = select(MatchRequestModel).where(MatchRequestModel.id == request_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_pending_for_user(self, user_id: UUID) -> list[MatchRequest]:
        stmt = (
            select(MatchRequestModel)
            .where(
                MatchRequestModel.receiver_id == user_id,
                MatchRequestModel.status == "pending",
            )
            .order_by(MatchRequestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_sent_by_user(self, user_id: UUID) -> list[MatchRequest]:
        stmt = (
            select(MatchRequestModel)
            .where(MatchRequestModel.sender_id == user_id)
            .order_by(MatchRequestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_pending_between(self, sender_id: UUID, receiver_id: UUID) -> MatchRequest | None:
        stmt = select(MatchRequestModel).where(
            and_(
                MatchRequestModel.sender_id == sender_id,
                MatchRequestModel.receiver_id == receiver_id,
                MatchRequestModel.status == "pending",
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, match_request: MatchRequest) -> MatchRequest:
        stmt = select(MatchRequestModel).where(MatchRequestModel.id == match_request.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import NotFoundError

            raise NotFoundError("Match request not found")

        model.status = match_request.status
        model.responded_at = match_request.responded_at
        model.proposed_start_date = match_request.proposed_start_date

        await self.session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: MatchRequestModel) -> MatchRequest:
        return MatchRequest(
            id=model.id,
            sender_id=model.sender_id,
            receiver_id=model.receiver_id,
            message=model.message,
            status=model.status,
            proposed_start_date=model.proposed_start_date,
            expires_at=model.expires_at,
            responded_at=model.responded_at,
            created_at=model.created_at,
        )
