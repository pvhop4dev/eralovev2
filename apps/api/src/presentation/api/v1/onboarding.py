"""Onboarding API Route.

POST /api/v1/users/me/onboarding — Complete onboarding
GET /api/v1/users/search — Search users by username
"""

from fastapi import APIRouter, Query

from application.dtos.auth_dto import UserResponse
from application.dtos.match_dto import OnboardingRequest
from infrastructure.database.repositories.user_repository import PostgresUserRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(tags=["Users"])


@router.post("/users/me/onboarding")
async def complete_onboarding(
    body: OnboardingRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Complete the onboarding wizard."""
    current_user.complete_onboarding(
        display_name=body.display_name,
        date_of_birth=body.date_of_birth,
        love_language=body.love_language,
        avatar_url=body.avatar_url,
    )

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
    return {"data": user_response.model_dump(), "meta": None, "error": None}


@router.get("/users/search")
async def search_users(
    current_user: CurrentUser,
    session: DbSession,
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
) -> dict:
    """Search users by username or display name."""
    user_repo = PostgresUserRepository(session)
    users = await user_repo.search(q, limit=20)

    # Exclude current user from results
    results = [
        {
            "id": str(u.id),
            "display_name": u.display_name,
            "username": u.username,
            "avatar_url": u.avatar_url,
            "zodiac_sign": u.zodiac_sign,
        }
        for u in users
        if u.id != current_user.id
    ]
    return {"data": {"users": results}, "meta": None, "error": None}
