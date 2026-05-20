"""Messages API Routes.

Chat message endpoints for a couple.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from domain.entities.message import MESSAGE_TYPES, Message
from domain.exceptions import CoupleNotFoundError, ForbiddenError, NotFoundError
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.message_repository import PostgresMessageRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/messages", tags=["Messages"])


class SendMessageRequest(BaseModel):
    content: str | None = None
    message_type: str = Field("text", description=f"One of: {', '.join(MESSAGE_TYPES)}")
    media_url: str | None = None
    reply_to_id: str | None = None


@router.post("", status_code=201)
async def send_message(
    body: SendMessageRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Send a new message."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    message = Message(
        id=uuid4(),
        couple_id=couple.id,
        sender_id=current_user.id,
        content=body.content,
        message_type=body.message_type,
        media_url=body.media_url,
        reply_to_id=UUID(body.reply_to_id) if body.reply_to_id else None,
    )

    msg_repo = PostgresMessageRepository(session)
    created = await msg_repo.create(message)
    return {"data": created.to_dict(), "meta": None, "error": None}


@router.get("")
async def get_messages(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = Query(None, description="Message ID for cursor pagination"),
) -> dict:
    """Get messages for current couple (newest first, paginated)."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    msg_repo = PostgresMessageRepository(session)
    before_id = UUID(before) if before else None
    messages = await msg_repo.get_by_couple(couple.id, limit, before_id)

    return {
        "data": {"messages": [m.to_dict() for m in messages]},
        "meta": {
            "count": len(messages),
            "has_more": len(messages) == limit,
        },
        "error": None,
    }


@router.post("/read")
async def mark_messages_read(
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Mark all partner's messages as read."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    msg_repo = PostgresMessageRepository(session)
    count = await msg_repo.mark_read_for_user(couple.id, current_user.id)

    return {"data": {"marked_read": count}, "meta": None, "error": None}


@router.post("/{message_id}/pin")
async def pin_message(
    message_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Pin/unpin a message (toggle)."""
    msg_repo = PostgresMessageRepository(session)
    message = await msg_repo.get_by_id(UUID(message_id))
    if not message:
        raise NotFoundError("Message not found")

    # Verify user belongs to couple
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != message.couple_id:
        raise ForbiddenError("Not your message")

    if message.is_pinned:
        message.unpin()
    else:
        message.pin()

    updated = await msg_repo.update(message)
    return {"data": updated.to_dict(), "meta": None, "error": None}


@router.get("/pinned")
async def get_pinned_messages(
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get all pinned messages for the couple."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    msg_repo = PostgresMessageRepository(session)
    pinned = await msg_repo.get_pinned(couple.id)

    return {
        "data": {"messages": [m.to_dict() for m in pinned]},
        "meta": {"count": len(pinned)},
        "error": None,
    }


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Soft delete a message."""
    msg_repo = PostgresMessageRepository(session)
    message = await msg_repo.get_by_id(UUID(message_id))
    if not message:
        raise NotFoundError("Message not found")

    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != message.couple_id:
        raise ForbiddenError("Not your message")

    message.soft_delete()
    await msg_repo.update(message)

    return {"data": {"deleted": True}, "meta": None, "error": None}
