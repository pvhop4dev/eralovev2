"""Events API Routes.

CRUD endpoints for love calendar events.
"""

from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from domain.entities.love_event import EVENT_TYPES, LoveEvent
from domain.exceptions import CoupleNotFoundError, ForbiddenError, NotFoundError
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.event_repository import PostgresLoveEventRepository
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from infrastructure.quotes.love_quotes import get_daily_quote
from infrastructure.services.calendar_helper import (
    get_current_weather,
    get_daily_feng_shui,
    get_lunar_date,
    get_zodiac_love_horoscope,
)
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/header")
async def get_calendar_header(
    current_user: CurrentUser,
    session: DbSession,
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
) -> dict:
    """Get aggregated data for the Calendar Header Widget.

    Includes lunar date, weather, love quote, days together,
    zodiac horoscope for both partners, and feng shui tips.
    """
    today_val = date.today()

    # 1. Base solar date details
    vietnamese_weekdays = {
        0: "Thứ Hai",
        1: "Thứ Ba",
        2: "Thứ Tư",
        3: "Thứ Năm",
        4: "Thứ Sáu",
        5: "Thứ Bảy",
        6: "Chủ Nhật",
    }
    weekday_idx = today_val.weekday()
    day_name = vietnamese_weekdays[weekday_idx]
    solar_formatted = f"{day_name}, {today_val.day} Tháng {today_val.month}, {today_val.year}"

    lunar_str = get_lunar_date(today_val)

    # 2. Fetch weather info
    weather_info = await get_current_weather(latitude, longitude)

    # 3. Fetch couple specific info
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)

    days_together = 0
    quote = get_daily_quote()
    partner_sign = None
    partner_name = "Người ấy"

    if couple:
        days_together = couple.days_together
        quote = get_daily_quote(str(couple.id))

        # Get partner info
        user_repo = PostgresUserRepository(session)
        partner_id = couple.get_partner_id(current_user.id)
        partner = await user_repo.get_by_id(partner_id)
        if partner:
            partner_sign = partner.zodiac_sign
            partner_name = partner.display_name

    # 4. Horoscopes
    user_horoscope = get_zodiac_love_horoscope(current_user.zodiac_sign, today_val)
    partner_horoscope = get_zodiac_love_horoscope(partner_sign, today_val) if partner_sign else None

    # 5. Feng Shui
    feng_shui_info = get_daily_feng_shui(today_val)

    return {
        "data": {
            "solar_date": {
                "iso": today_val.isoformat(),
                "day_name": day_name,
                "formatted": solar_formatted,
            },
            "lunar_date": lunar_str,
            "weather": weather_info,
            "daily_quote": quote,
            "days_together": days_together,
            "horoscope": {
                "user": {"sign": current_user.zodiac_sign, "prediction": user_horoscope},
                "partner": {
                    "name": partner_name,
                    "sign": partner_sign,
                    "prediction": partner_horoscope,
                }
                if partner_sign
                else None,
            },
            "feng_shui": feng_shui_info,
        },
        "meta": None,
        "error": None,
    }


class CreateEventRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event_type: str = Field(..., description=f"One of: {', '.join(EVENT_TYPES)}")
    event_date: date
    event_time: str | None = Field(None, description="HH:MM format")
    end_date: date | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    color: str | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None
    reminder_before: str | None = None


class UpdateEventRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    event_type: str | None = None
    event_date: date | None = None
    event_time: str | None = None
    end_date: date | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    color: str | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None
    reminder_before: str | None = None


@router.post("", status_code=201)
async def create_event(
    body: CreateEventRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Create a new love event."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    from datetime import time as time_cls

    event_time = None
    if body.event_time:
        parts = body.event_time.split(":")
        event_time = time_cls(int(parts[0]), int(parts[1]))

    event = LoveEvent(
        id=uuid4(),
        couple_id=couple.id,
        created_by=current_user.id,
        title=body.title,
        description=body.description,
        event_type=body.event_type,
        event_date=body.event_date,
        event_time=event_time,
        end_date=body.end_date,
        location_name=body.location_name,
        latitude=body.latitude,
        longitude=body.longitude,
        color=body.color,
        is_recurring=body.is_recurring,
        recurrence_rule=body.recurrence_rule,
        reminder_before=body.reminder_before,
    )

    event_repo = PostgresLoveEventRepository(session)
    created = await event_repo.create(event)
    return {"data": created.to_dict(), "meta": None, "error": None}


@router.get("")
async def get_events(
    current_user: CurrentUser,
    session: DbSession,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
) -> dict:
    """Get events for a specific month."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    event_repo = PostgresLoveEventRepository(session)
    events = await event_repo.get_by_couple_and_month(couple.id, year, month)
    return {
        "data": {"events": [e.to_dict() for e in events]},
        "meta": {"year": year, "month": month, "count": len(events)},
        "error": None,
    }


@router.get("/upcoming")
async def get_upcoming_events(
    current_user: CurrentUser,
    session: DbSession,
    days: int = Query(7, ge=1, le=90),
) -> dict:
    """Get upcoming events within N days."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    event_repo = PostgresLoveEventRepository(session)
    events = await event_repo.get_upcoming(couple.id, days)
    return {
        "data": {"events": [e.to_dict() for e in events]},
        "meta": {"days": days, "count": len(events)},
        "error": None,
    }


@router.get("/{event_id}")
async def get_event(
    event_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get a single event by ID."""
    event_repo = PostgresLoveEventRepository(session)
    event = await event_repo.get_by_id(UUID(event_id))
    if not event:
        raise NotFoundError("Event not found")

    # Verify user belongs to this couple
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != event.couple_id:
        raise ForbiddenError("You don't have access to this event")

    return {"data": event.to_dict(), "meta": None, "error": None}


@router.patch("/{event_id}")
async def update_event(
    event_id: str,
    body: UpdateEventRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Update an existing event."""
    event_repo = PostgresLoveEventRepository(session)
    event = await event_repo.get_by_id(UUID(event_id))
    if not event:
        raise NotFoundError("Event not found")

    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != event.couple_id:
        raise ForbiddenError("You don't have access to this event")

    from datetime import time as time_cls

    event_time = None
    if body.event_time:
        parts = body.event_time.split(":")
        event_time = time_cls(int(parts[0]), int(parts[1]))

    update_data = body.model_dump(exclude_unset=True, exclude={"event_time"})
    if event_time is not None:
        update_data["event_time"] = event_time

    event.update(**update_data)
    updated = await event_repo.update(event)
    return {"data": updated.to_dict(), "meta": None, "error": None}


@router.delete("/{event_id}", status_code=200)
async def delete_event(
    event_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Soft delete an event."""
    event_repo = PostgresLoveEventRepository(session)
    event = await event_repo.get_by_id(UUID(event_id))
    if not event:
        raise NotFoundError("Event not found")

    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != event.couple_id:
        raise ForbiddenError("You don't have access to this event")

    await event_repo.soft_delete(UUID(event_id))
    return {"data": {"deleted": True}, "meta": None, "error": None}
