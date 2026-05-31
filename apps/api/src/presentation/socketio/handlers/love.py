"""Love Touch Socket.IO Event Handlers.

Handles real-time haptic/animation interactions between couples.
"""

from datetime import UTC, datetime

import structlog

from presentation.socketio.server import sio

logger = structlog.get_logger(__name__)


@sio.on("love:touch")
async def handle_love_touch(sid: str, data: dict) -> None:
    """Handle love touch interaction, broadcasting haptic event to partner."""
    async with sio.session(sid) as session:
        user_id = session.get("user_id")
        couple_id = session.get("couple_id")
        display_name = session.get("display_name")

    if not user_id or not couple_id:
        logger.warn("ws_love_touch_rejected", sid=sid, reason="Unauthorized")
        return

    intensity = data.get("intensity", "normal")  # normal | strong

    couple_room = f"couple:{couple_id}"
    await sio.emit(
        "love:touch",
        {
            "sender_id": user_id,
            "sender_name": display_name,
            "intensity": intensity,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        room=couple_room,
        skip_sid=sid,
    )
    logger.info("ws_love_touch_broadcasted", user_id=user_id, couple_id=couple_id, intensity=intensity)
