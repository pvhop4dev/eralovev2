"""Add Photo Use Case.

Handles registering a new photo metadata in the system.
"""

from uuid import UUID, uuid4
import structlog

from application.dtos.photo_dto import AddPhotoRequest, PhotoResponse
from domain.entities.photo import Photo
from domain.exceptions import CoupleNotFoundError, ForbiddenError, NotFoundError
from domain.repositories.photo_repository import PhotoRepository
from domain.repositories.event_repository import LoveEventRepository

logger = structlog.get_logger()


class AddPhotoUseCase:
    """Use case to add a new photo to a couple space or calendar event."""

    def __init__(
        self,
        photo_repo: PhotoRepository,
        event_repo: LoveEventRepository,
    ) -> None:
        self.photo_repo = photo_repo
        self.event_repo = event_repo

    async def execute(
        self,
        request: AddPhotoRequest,
        uploaded_by: UUID,
        couple_id: UUID,
    ) -> PhotoResponse:
        """Execute the photo addition.

        Args:
            request: The add photo request details.
            uploaded_by: ID of the user uploading the photo.
            couple_id: ID of the active couple space.

        Returns:
            PhotoResponse DTO.
        """
        event_uuid = None
        if request.event_id:
            event_uuid = UUID(request.event_id)
            # Verify event exists and belongs to the couple
            event = await self.event_repo.get_by_id(event_uuid)
            if not event:
                raise NotFoundError("Calendar event not found")
            if event.couple_id != couple_id:
                raise ForbiddenError("Calendar event does not belong to your couple space")

        photo_entity = Photo(
            id=uuid4(),
            couple_id=couple_id,
            uploaded_by=uploaded_by,
            event_id=event_uuid,
            s3_key=request.s3_key,
            thumbnail_key=request.thumbnail_key,
            original_url=request.original_url,
            thumbnail_url=request.thumbnail_url,
            caption=request.caption,
            photo_date=request.photo_date,
            location_name=request.location_name,
            latitude=request.latitude,
            longitude=request.longitude,
            width=request.width,
            height=request.height,
            file_size=request.file_size,
            mime_type=request.mime_type,
            exif_data=request.exif_data,
        )

        created_photo = await self.photo_repo.create(photo_entity)

        logger.info(
            "photo_added",
            photo_id=str(created_photo.id),
            uploaded_by=str(uploaded_by),
            couple_id=str(couple_id),
            event_id=str(event_uuid) if event_uuid else None,
        )

        return PhotoResponse(
            id=str(created_photo.id),
            couple_id=str(created_photo.couple_id),
            uploaded_by=str(created_photo.uploaded_by),
            event_id=str(created_photo.event_id) if created_photo.event_id else None,
            s3_key=created_photo.s3_key,
            thumbnail_key=created_photo.thumbnail_key,
            original_url=created_photo.original_url,
            thumbnail_url=created_photo.thumbnail_url,
            caption=created_photo.caption,
            photo_date=created_photo.photo_date.isoformat() if created_photo.photo_date else None,
            location_name=created_photo.location_name,
            latitude=created_photo.latitude,
            longitude=created_photo.longitude,
            width=created_photo.width,
            height=created_photo.height,
            file_size=created_photo.file_size,
            mime_type=created_photo.mime_type,
            exif_data=created_photo.exif_data,
            created_at=created_photo.created_at.isoformat() if created_photo.created_at else None,
        )
