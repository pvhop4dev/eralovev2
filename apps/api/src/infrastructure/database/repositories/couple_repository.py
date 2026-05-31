"""PostgreSQL Couple Repository Implementation."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.couple import Couple
from domain.repositories.couple_repository import CoupleRepository
from infrastructure.database.models.couple_model import CoupleModel


class PostgresCoupleRepository(CoupleRepository):
    """PostgreSQL-backed couple repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, couple: Couple) -> Couple:
        model = CoupleModel(
            id=couple.id,
            user1_id=couple.user1_id,
            user2_id=couple.user2_id,
            start_date=couple.start_date,
            couple_photo_url=couple.couple_photo_url,
            status=couple.status,
            theme_color=couple.theme_color,
            wallpaper_url=couple.wallpaper_url,
            nicknames=couple.nicknames,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, couple_id: UUID) -> Couple | None:
        stmt = select(CoupleModel).where(CoupleModel.id == couple_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_active_for_user(self, user_id: UUID) -> Couple | None:
        stmt = select(CoupleModel).where(
            or_(
                CoupleModel.user1_id == user_id,
                CoupleModel.user2_id == user_id,
            ),
            CoupleModel.status.in_(["active", "paused"]),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, couple: Couple) -> Couple:
        stmt = select(CoupleModel).where(CoupleModel.id == couple.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import CoupleNotFoundError

            raise CoupleNotFoundError()

        model.couple_photo_url = couple.couple_photo_url
        model.status = couple.status
        model.theme_color = couple.theme_color
        model.wallpaper_url = couple.wallpaper_url
        model.nicknames = couple.nicknames
        model.paused_at = couple.paused_at
        model.broken_up_at = couple.broken_up_at

        await self.session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: CoupleModel) -> Couple:
        return Couple(
            id=model.id,
            user1_id=model.user1_id,
            user2_id=model.user2_id,
            start_date=model.start_date,
            couple_photo_url=model.couple_photo_url,
            status=model.status,
            theme_color=model.theme_color,
            wallpaper_url=model.wallpaper_url,
            nicknames=model.nicknames,
            created_at=model.created_at,
            updated_at=model.updated_at,
            paused_at=model.paused_at,
            broken_up_at=model.broken_up_at,
        )
