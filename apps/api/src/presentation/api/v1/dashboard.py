"""Dashboard API Route.

GET /api/v1/dashboard — Aggregated dashboard data
"""

from fastapi import APIRouter

from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from infrastructure.quotes.love_quotes import get_daily_quote
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get aggregated dashboard data.

    Returns couple info, partner, daily quote, and user's mood status.
    """
    couple_repo = PostgresCoupleRepository(session)
    user_repo = PostgresUserRepository(session)

    # Get couple
    couple = await couple_repo.get_active_for_user(current_user.id)

    dashboard_data: dict = {
        "user": {
            "id": str(current_user.id),
            "display_name": current_user.display_name,
            "avatar_url": current_user.avatar_url,
            "zodiac_sign": current_user.zodiac_sign,
            "is_onboarded": current_user.is_onboarded,
        },
        "couple": None,
        "partner": None,
        "daily_quote": get_daily_quote(),
        "days_together": 0,
        "upcoming_events": [],
        "memory_flashback": [],
    }

    if couple:
        # Get partner info
        partner_id = couple.get_partner_id(current_user.id)
        partner = await user_repo.get_by_id(partner_id)

        dashboard_data["couple"] = {
            "id": str(couple.id),
            "start_date": couple.start_date.isoformat(),
            "status": couple.status,
            "theme_color": couple.theme_color,
            "couple_photo_url": couple.couple_photo_url,
            "nicknames": couple.nicknames,
        }
        dashboard_data["days_together"] = couple.days_together
        dashboard_data["daily_quote"] = get_daily_quote(str(couple.id))

        if partner:
            dashboard_data["partner"] = {
                "id": str(partner.id),
                "display_name": partner.display_name,
                "username": partner.username,
                "avatar_url": partner.avatar_url,
                "zodiac_sign": partner.zodiac_sign,
            }

        # Get upcoming and memory flashback events
        from infrastructure.database.repositories.event_repository import (
            PostgresLoveEventRepository,
        )

        event_repo = PostgresLoveEventRepository(session)
        upcoming = await event_repo.get_upcoming(couple.id, 7)
        flashback = await event_repo.get_past_events_on_this_day(couple.id)

        dashboard_data["upcoming_events"] = [e.to_dict() for e in upcoming]
        dashboard_data["memory_flashback"] = [e.to_dict() for e in flashback]

    return {"data": dashboard_data, "meta": None, "error": None}
