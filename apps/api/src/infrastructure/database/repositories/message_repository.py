"""PostgreSQL Message Repository Implementation."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.message import Message
from domain.repositories.message_repository import MessageRepository
from infrastructure.database.models.message_model import MessageModel


class PostgresMessageRepository(MessageRepository):
    """PostgreSQL-backed message repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, message: Message) -> Message:
        model = MessageModel(
            id=message.id,
            couple_id=message.couple_id,
            sender_id=message.sender_id,
            content=message.content,
            message_type=message.message_type,
            media_url=message.media_url,
            media_metadata=message.media_metadata,
            reply_to_id=message.reply_to_id,
            is_pinned=message.is_pinned,
            status=message.status,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = select(MessageModel).where(
            MessageModel.id == message_id,
            MessageModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_couple(
        self, couple_id: UUID, limit: int = 50, before_id: UUID | None = None
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(
                MessageModel.couple_id == couple_id,
                MessageModel.deleted_at.is_(None),
            )
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        if before_id:
            # Cursor-based pagination
            subq = select(MessageModel.created_at).where(MessageModel.id == before_id).scalar_subquery()
            stmt = stmt.where(MessageModel.created_at < subq)

        result = await self.session.execute(stmt)
        messages = [self._to_entity(m) for m in result.scalars().all()]
        # Return in chronological order
        return list(reversed(messages))

    async def get_pinned(self, couple_id: UUID) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(
                MessageModel.couple_id == couple_id,
                MessageModel.is_pinned.is_(True),
                MessageModel.deleted_at.is_(None),
            )
            .order_by(MessageModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, message: Message) -> Message:
        stmt = select(MessageModel).where(MessageModel.id == message.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import NotFoundError
            raise NotFoundError("Message not found")

        model.is_pinned = message.is_pinned
        model.status = message.status
        model.delivered_at = message.delivered_at
        model.read_at = message.read_at
        model.deleted_at = message.deleted_at

        await self.session.flush()
        return self._to_entity(model)

    async def mark_read_for_user(self, couple_id: UUID, reader_id: UUID) -> int:
        """Mark all unread messages as read (messages NOT sent by reader)."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(MessageModel)
            .where(
                MessageModel.couple_id == couple_id,
                MessageModel.sender_id != reader_id,
                MessageModel.status.in_(["sent", "delivered"]),
                MessageModel.deleted_at.is_(None),
            )
            .values(status="read", read_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount  # type: ignore[return-value]

    @staticmethod
    def _to_entity(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            couple_id=model.couple_id,
            sender_id=model.sender_id,
            content=model.content,
            message_type=model.message_type,
            media_url=model.media_url,
            media_metadata=model.media_metadata,
            reply_to_id=model.reply_to_id,
            is_pinned=model.is_pinned,
            status=model.status,
            delivered_at=model.delivered_at,
            read_at=model.read_at,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )
