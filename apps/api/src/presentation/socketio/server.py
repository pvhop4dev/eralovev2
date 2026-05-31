"""Socket.IO Server Initialization.

Sets up the AsyncServer and registers connection and lifecycle events.
"""


import socketio
import structlog

from domain.exceptions import DomainError
from infrastructure.auth.jwt_handler import get_user_id_from_token
from infrastructure.config import get_settings
from infrastructure.database.connection import async_session_maker
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.user_repository import PostgresUserRepository

settings = get_settings()
logger = structlog.get_logger(__name__)

# Configure client manager (Redis for scaling, fallback to in-memory)
client_manager = None
if settings.REDIS_URL:
    client_manager = socketio.AsyncRedisManager(settings.REDIS_URL)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    client_manager=client_manager,
    logger=True,
    engineio_logger=False,
    ping_timeout=20,
    ping_interval=25,
)


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None) -> None:
    """Handle connection from client, authenticate with JWT token."""
    logger.info("ws_connect_attempt", sid=sid)
    if not auth or "token" not in auth:
        logger.warn("ws_connect_rejected", sid=sid, reason="Missing auth token")
        raise socketio.exceptions.ConnectionRefusedError("Missing auth token")

    token = auth["token"]
    try:
        user_id = get_user_id_from_token(token, expected_type="access")
    except DomainError as e:
        logger.warn("ws_connect_rejected", sid=sid, reason="Invalid token", error=str(e))
        raise socketio.exceptions.ConnectionRefusedError("Invalid token") from e

    # Fetch user and active couple
    async with async_session_maker() as db_session:
        user_repo = PostgresUserRepository(db_session)
        couple_repo = PostgresCoupleRepository(db_session)

        user = await user_repo.get_by_id(user_id)
        if not user:
            logger.warn("ws_connect_rejected", sid=sid, reason="User not found", user_id=str(user_id))
            raise socketio.exceptions.ConnectionRefusedError("Unauthorized")

        couple = await couple_repo.get_active_for_user(user_id)
        if not couple:
            logger.warn("ws_connect_rejected", sid=sid, reason="No active couple", user_id=str(user_id))
            raise socketio.exceptions.ConnectionRefusedError("No active couple")

    # Store user context in session
    async with sio.session(sid) as session:
        session["user_id"] = str(user.id)
        session["couple_id"] = str(couple.id)
        session["display_name"] = user.display_name

    # Join rooms
    couple_room = f"couple:{couple.id}"
    user_room = f"user:{user.id}"
    await sio.enter_room(sid, couple_room)
    await sio.enter_room(sid, user_room)

    # Notify partner about online status
    await sio.emit(
        "partner_online",
        {
            "user_id": str(user.id),
            "display_name": user.display_name,
        },
        room=couple_room,
        skip_sid=sid,
    )

    logger.info("ws_connected", sid=sid, user_id=str(user.id), couple_id=str(couple.id))


@sio.event
async def disconnect(sid: str) -> None:
    """Handle client disconnect."""
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
        couple_id = session.get("couple_id")

    if couple_id and user_id:
        couple_room = f"couple:{couple_id}"
        await sio.emit(
            "partner_offline",
            {
                "user_id": user_id,
            },
            room=couple_room,
            skip_sid=sid,
        )

    logger.info("ws_disconnected", sid=sid, user_id=user_id, couple_id=couple_id)


# Import handlers to register events
import presentation.socketio.handlers.chat  # noqa: E402
import presentation.socketio.handlers.love  # noqa: F401, E402

