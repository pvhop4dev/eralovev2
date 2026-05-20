"""Couple API Routes.

GET /api/v1/couple — Get current couple info
PATCH /api/v1/couple — Update couple settings
"""

from fastapi import APIRouter

from application.dtos.match_dto import CoupleResponse, UpdateCoupleDTO
from domain.exceptions import CoupleNotFoundError
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/couple", tags=["Couple"])


@router.get("")
async def get_couple(
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get the current couple info and partner details."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    # Get partner info
    partner_id = couple.get_partner_id(current_user.id)
    user_repo = PostgresUserRepository(session)
    partner = await user_repo.get_by_id(partner_id)

    couple_response = CoupleResponse(
        id=str(couple.id),
        user1_id=str(couple.user1_id),
        user2_id=str(couple.user2_id),
        start_date=couple.start_date,
        couple_photo_url=couple.couple_photo_url,
        status=couple.status,
        theme_color=couple.theme_color,
        wallpaper_url=couple.wallpaper_url,
        nicknames=couple.nicknames,
        days_together=couple.days_together,
    )

    return {
        "data": {
            "couple": couple_response.model_dump(),
            "partner": {
                "id": str(partner.id),
                "display_name": partner.display_name,
                "username": partner.username,
                "avatar_url": partner.avatar_url,
                "zodiac_sign": partner.zodiac_sign,
            } if partner else None,
        },
        "meta": None,
        "error": None,
    }


@router.patch("")
async def update_couple(
    body: UpdateCoupleDTO,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Update couple settings (photo, theme, wallpaper, nicknames)."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    update_data = body.model_dump(exclude_unset=True)
    couple.update_settings(**update_data)
    updated = await couple_repo.update(couple)

    couple_response = CoupleResponse(
        id=str(updated.id),
        user1_id=str(updated.user1_id),
        user2_id=str(updated.user2_id),
        start_date=updated.start_date,
        couple_photo_url=updated.couple_photo_url,
        status=updated.status,
        theme_color=updated.theme_color,
        wallpaper_url=updated.wallpaper_url,
        nicknames=updated.nicknames,
        days_together=updated.days_together,
    )
    return {"data": couple_response.model_dump(), "meta": None, "error": None}
