"""Users API Routes.

GET /api/v1/users/me — Get current user profile
PATCH /api/v1/users/me — Update current user profile
"""

from fastapi import APIRouter

from application.dtos.auth_dto import UpdateUserRequest, UserResponse
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_current_user_profile(
    current_user: CurrentUser,
) -> dict:
    """Get the authenticated user's profile."""
    user_response = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        username=current_user.username,
        avatar_url=current_user.avatar_url,
        date_of_birth=current_user.date_of_birth,
        gender=current_user.gender,
        zodiac_sign=current_user.zodiac_sign,
        love_language=current_user.love_language,
        bio=current_user.bio,
        is_email_verified=current_user.is_email_verified,
        is_onboarded=current_user.is_onboarded,
    )
    return {
        "data": user_response.model_dump(),
        "meta": None,
        "error": None,
    }


@router.patch("/me")
async def update_current_user_profile(
    body: UpdateUserRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Update the authenticated user's profile."""
    # Apply partial updates
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    # Recalculate zodiac if DOB changed
    if "date_of_birth" in update_data and current_user.date_of_birth:
        from domain.entities.user import _calculate_zodiac
        current_user.zodiac_sign = _calculate_zodiac(current_user.date_of_birth)

    user_repo = PostgresUserRepository(session)
    updated = await user_repo.update(current_user)

    user_response = UserResponse(
        id=str(updated.id),
        email=updated.email,
        display_name=updated.display_name,
        username=updated.username,
        avatar_url=updated.avatar_url,
        date_of_birth=updated.date_of_birth,
        gender=updated.gender,
        zodiac_sign=updated.zodiac_sign,
        love_language=updated.love_language,
        bio=updated.bio,
        is_email_verified=updated.is_email_verified,
        is_onboarded=updated.is_onboarded,
    )
    return {
        "data": user_response.model_dump(),
        "meta": None,
        "error": None,
    }
