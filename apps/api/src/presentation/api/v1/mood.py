"""Mood Check-in API Routes.

POST /api/v1/mood/checkin — Submit daily mood
GET /api/v1/mood/today — Get today's mood
"""

from datetime import UTC, date, datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from presentation.deps import RedisClient
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/mood", tags=["Mood"])


class MoodCheckinRequest(BaseModel):
    mood_emoji: str = Field(..., max_length=10, description="Mood emoji")
    mood_note: str | None = Field(None, max_length=200)


@router.post("/checkin")
async def submit_mood(
    body: MoodCheckinRequest,
    current_user: CurrentUser,
    redis: RedisClient,
) -> dict:
    """Submit today's mood check-in.

    Stored in Redis with 24h TTL for quick access.
    """
    today = date.today().isoformat()
    mood_key = f"eralove:mood:{current_user.id}:{today}"
    mood_data = f"{body.mood_emoji}|{body.mood_note or ''}"
    await redis.setex(mood_key, 86400, mood_data)  # 24h TTL

    return {
        "data": {
            "mood_emoji": body.mood_emoji,
            "mood_note": body.mood_note,
            "checked_in_at": datetime.now(UTC).isoformat(),
        },
        "meta": None,
        "error": None,
    }


@router.get("/today")
async def get_today_mood(
    current_user: CurrentUser,
    redis: RedisClient,
) -> dict:
    """Get today's mood for the current user."""
    today = date.today().isoformat()
    mood_key = f"eralove:mood:{current_user.id}:{today}"
    mood_data = await redis.get(mood_key)

    if mood_data:
        parts = mood_data.split("|", 1)
        return {
            "data": {
                "mood_emoji": parts[0],
                "mood_note": parts[1] if len(parts) > 1 and parts[1] else None,
                "has_checked_in": True,
            },
            "meta": None,
            "error": None,
        }

    return {
        "data": {"mood_emoji": None, "mood_note": None, "has_checked_in": False},
        "meta": None,
        "error": None,
    }
