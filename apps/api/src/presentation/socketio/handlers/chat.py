"""Chat Socket.IO Event Handlers.

Handles events like sending messages, typing status, and read receipts.
"""

from uuid import UUID, uuid4

import structlog

from domain.entities.message import MESSAGE_TYPES, Message
from infrastructure.database.connection import async_session_maker
from infrastructure.database.repositories.message_repository import PostgresMessageRepository
from presentation.socketio.server import sio

logger = structlog.get_logger(__name__)


@sio.on("chat:message")
async def handle_message(sid: str, data: dict) -> None:
    """Handle incoming message from WebSocket, save to DB, and broadcast."""
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
        couple_id = session.get("couple_id")

    if not user_id or not couple_id:
        logger.warn("ws_chat_message_rejected", sid=sid, reason="Unauthorized")
        await sio.emit("error", {"message": "Unauthorized"}, to=sid)
        return

    content = data.get("content")
    message_type = data.get("message_type", "text")
    media_url = data.get("media_url")
    reply_to_id_str = data.get("reply_to_id")

    if message_type not in MESSAGE_TYPES:
        await sio.emit(
            "error", {"message": f"Invalid message type. Must be one of: {MESSAGE_TYPES}"}, to=sid
        )
        return

    reply_to_id = None
    if reply_to_id_str:
        try:
            reply_to_id = UUID(reply_to_id_str)
        except ValueError:
            await sio.emit("error", {"message": "Invalid reply_to_id UUID format"}, to=sid)
            return

    # Save to database
    try:
        async with async_session_maker() as db_session:
            msg_repo = PostgresMessageRepository(db_session)
            message = Message(
                id=uuid4(),
                couple_id=UUID(couple_id),
                sender_id=UUID(user_id),
                content=content,
                message_type=message_type,
                media_url=media_url,
                reply_to_id=reply_to_id,
            )
            created = await msg_repo.create(message)
            await db_session.commit()
            created_dict = created.to_dict()
    except Exception as e:
        logger.error("ws_chat_message_db_error", sid=sid, user_id=user_id, error=str(e))
        await sio.emit("error", {"message": "Failed to save message to database"}, to=sid)
        return

    # Broadcast to couple room (both users)
    couple_room = f"couple:{couple_id}"
    await sio.emit(
        "chat:message",
        created_dict,
        room=couple_room,
    )
    logger.info("ws_chat_message_broadcasted", message_id=str(message.id), couple_id=couple_id)


@sio.on("chat:typing")
async def handle_typing(sid: str, data: dict) -> None:
    """Broadcast typing indicator to partner."""
    async with sio.session(sid) as session:
        couple_id = session.get("couple_id")
        user_id = session.get("user_id")

    if not couple_id or not user_id:
        return

    is_typing = data.get("is_typing", True)

    couple_room = f"couple:{couple_id}"
    await sio.emit(
        "chat:typing",
        {
            "user_id": user_id,
            "is_typing": is_typing,
        },
        room=couple_room,
        skip_sid=sid,
    )


@sio.on("chat:read")
async def handle_read(sid: str, data: dict | None = None) -> None:
    """Mark all unread messages in the couple as read for current user."""
    async with sio.session(sid) as session:
        couple_id = session.get("couple_id")
        user_id = session.get("user_id")

    if not couple_id or not user_id:
        return

    try:
        async with async_session_maker() as db_session:
            msg_repo = PostgresMessageRepository(db_session)
            count = await msg_repo.mark_read_for_user(UUID(couple_id), UUID(user_id))
            await db_session.commit()
    except Exception as e:
        logger.error("ws_chat_read_db_error", sid=sid, user_id=user_id, error=str(e))
        return

    couple_room = f"couple:{couple_id}"
    await sio.emit(
        "chat:read",
        {
            "reader_id": user_id,
            "marked_read": count,
        },
        room=couple_room,
        skip_sid=sid,
    )
    logger.info("ws_chat_read_broadcasted", user_id=user_id, couple_id=couple_id, count=count)
