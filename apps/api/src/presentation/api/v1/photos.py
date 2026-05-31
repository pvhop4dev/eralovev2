"""Photos API Routes.

Endpoints for uploading/saving photo details, listing photos, and deleting photos.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from application.dtos.photo_dto import AddPhotoRequest, PhotoResponse
from application.use_cases.photo.add_photo import AddPhotoUseCase
from application.use_cases.photo.delete_photo import DeletePhotoUseCase
from domain.exceptions import CoupleNotFoundError, ForbiddenError, NotFoundError
from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.event_repository import PostgresLoveEventRepository
from infrastructure.database.repositories.photo_repository import PostgresPhotoRepository
from presentation.deps import DbSession
from presentation.middleware.auth_middleware import CurrentUser

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("", status_code=201)
async def add_photo(
    body: AddPhotoRequest,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Save metadata for an uploaded photo."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    photo_repo = PostgresPhotoRepository(session)
    event_repo = PostgresLoveEventRepository(session)
    
    use_case = AddPhotoUseCase(photo_repo, event_repo)
    response = await use_case.execute(body, current_user.id, couple.id)

    return {"data": response.model_dump(), "meta": None, "error": None}


@router.get("")
async def get_photos(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(50, ge=1, le=100),
    before: str | None = Query(None, description="Photo ID for cursor pagination"),
) -> dict:
    """Get photos for the couple's general album (newest first, paginated)."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    photo_repo = PostgresPhotoRepository(session)
    before_id = UUID(before) if before else None
    
    photos = await photo_repo.get_by_couple(couple.id, limit, before_id)
    
    # We want to return PhotoResponse serialization
    photo_responses = []
    for p in photos:
        photo_responses.append(
            PhotoResponse(
                id=str(p.id),
                couple_id=str(p.couple_id),
                uploaded_by=str(p.uploaded_by),
                event_id=str(p.event_id) if p.event_id else None,
                s3_key=p.s3_key,
                thumbnail_key=p.thumbnail_key,
                original_url=p.original_url,
                thumbnail_url=p.thumbnail_url,
                caption=p.caption,
                photo_date=p.photo_date.isoformat() if p.photo_date else None,
                location_name=p.location_name,
                latitude=p.latitude,
                longitude=p.longitude,
                width=p.width,
                height=p.height,
                file_size=p.file_size,
                mime_type=p.mime_type,
                exif_data=p.exif_data,
                created_at=p.created_at.isoformat() if p.created_at else None,
            ).model_dump()
        )

    return {
        "data": {"photos": photo_responses},
        "meta": {
            "count": len(photos),
            "has_more": len(photos) == limit,
        },
        "error": None,
    }


@router.get("/event/{event_id}")
async def get_event_photos(
    event_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Get all photos attached to a specific event."""
    event_uuid = UUID(event_id)
    
    # Verify event exists and belongs to the couple
    event_repo = PostgresLoveEventRepository(session)
    event = await event_repo.get_by_id(event_uuid)
    if not event:
        raise NotFoundError("Event not found")

    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple or couple.id != event.couple_id:
        raise ForbiddenError("You don't have access to this event")

    photo_repo = PostgresPhotoRepository(session)
    photos = await photo_repo.get_by_event(event_uuid)

    photo_responses = []
    for p in photos:
        photo_responses.append(
            PhotoResponse(
                id=str(p.id),
                couple_id=str(p.couple_id),
                uploaded_by=str(p.uploaded_by),
                event_id=str(p.event_id) if p.event_id else None,
                s3_key=p.s3_key,
                thumbnail_key=p.thumbnail_key,
                original_url=p.original_url,
                thumbnail_url=p.thumbnail_url,
                caption=p.caption,
                photo_date=p.photo_date.isoformat() if p.photo_date else None,
                location_name=p.location_name,
                latitude=p.latitude,
                longitude=p.longitude,
                width=p.width,
                height=p.height,
                file_size=p.file_size,
                mime_type=p.mime_type,
                exif_data=p.exif_data,
                created_at=p.created_at.isoformat() if p.created_at else None,
            ).model_dump()
        )

    return {
        "data": {"photos": photo_responses},
        "meta": {"count": len(photos)},
        "error": None,
    }


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> dict:
    """Soft delete a photo."""
    couple_repo = PostgresCoupleRepository(session)
    couple = await couple_repo.get_active_for_user(current_user.id)
    if not couple:
        raise CoupleNotFoundError()

    photo_repo = PostgresPhotoRepository(session)
    use_case = DeletePhotoUseCase(photo_repo)
    await use_case.execute(UUID(photo_id), current_user.id, couple.id)

    return {"data": {"deleted": True}, "meta": None, "error": None}
