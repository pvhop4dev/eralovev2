"""PostgreSQL LoveEvent Repository Implementation."""

import calendar
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.love_event import LoveEvent
from domain.repositories.event_repository import LoveEventRepository
from infrastructure.database.models.love_event_model import LoveEventModel


class PostgresLoveEventRepository(LoveEventRepository):
    """PostgreSQL-backed love event repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: LoveEvent) -> LoveEvent:
        model = LoveEventModel(
            id=event.id,
            couple_id=event.couple_id,
            created_by=event.created_by,
            title=event.title,
            description=event.description,
            event_type=event.event_type,
            event_date=event.event_date,
            event_time=event.event_time,
            end_date=event.end_date,
            location_name=event.location_name,
            latitude=event.latitude,
            longitude=event.longitude,
            color=event.color,
            icon=event.icon,
            is_recurring=event.is_recurring,
            recurrence_rule=event.recurrence_rule,
            reminder_before=event.reminder_before,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, event_id: UUID) -> LoveEvent | None:
        stmt = select(LoveEventModel).where(
            LoveEventModel.id == event_id,
            LoveEventModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_couple_and_month(
        self, couple_id: UUID, year: int, month: int
    ) -> list[LoveEvent]:
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        stmt = (
            select(LoveEventModel)
            .where(
                LoveEventModel.couple_id == couple_id,
                LoveEventModel.event_date >= first_day,
                LoveEventModel.event_date <= last_day,
                LoveEventModel.deleted_at.is_(None),
            )
            .order_by(LoveEventModel.event_date, LoveEventModel.event_time)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_upcoming(self, couple_id: UUID, days: int = 7) -> list[LoveEvent]:
        today = date.today()
        end = today + timedelta(days=days)

        stmt = (
            select(LoveEventModel)
            .where(
                LoveEventModel.couple_id == couple_id,
                LoveEventModel.event_date >= today,
                LoveEventModel.event_date <= end,
                LoveEventModel.deleted_at.is_(None),
            )
            .order_by(LoveEventModel.event_date, LoveEventModel.event_time)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, event: LoveEvent) -> LoveEvent:
        stmt = select(LoveEventModel).where(LoveEventModel.id == event.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import NotFoundError
            raise NotFoundError("Event not found")

        model.title = event.title
        model.description = event.description
        model.event_type = event.event_type
        model.event_date = event.event_date
        model.event_time = event.event_time
        model.end_date = event.end_date
        model.location_name = event.location_name
        model.color = event.color
        model.icon = event.icon
        model.reminder_before = event.reminder_before

        await self.session.flush()
        return self._to_entity(model)

    async def soft_delete(self, event_id: UUID) -> None:
        stmt = select(LoveEventModel).where(LoveEventModel.id == event_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def get_past_events_on_this_day(self, couple_id: UUID) -> list[LoveEvent]:
        today = date.today()
        stmt = (
            select(LoveEventModel)
            .where(
                LoveEventModel.couple_id == couple_id,
                extract("month", LoveEventModel.event_date) == today.month,
                extract("day", LoveEventModel.event_date) == today.day,
                LoveEventModel.event_date < today,
                LoveEventModel.deleted_at.is_(None),
            )
            .order_by(LoveEventModel.event_date.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]


    @staticmethod
    def _to_entity(model: LoveEventModel) -> LoveEvent:
        return LoveEvent(
            id=model.id,
            couple_id=model.couple_id,
            created_by=model.created_by,
            title=model.title,
            description=model.description,
            event_type=model.event_type,
            event_date=model.event_date,
            event_time=model.event_time,
            end_date=model.end_date,
            location_name=model.location_name,
            latitude=float(model.latitude) if model.latitude else None,
            longitude=float(model.longitude) if model.longitude else None,
            color=model.color,
            icon=model.icon,
            is_recurring=model.is_recurring,
            recurrence_rule=model.recurrence_rule,
            reminder_before=model.reminder_before,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
