"""Delete Photo Use Case.

Handles soft deleting a photo in the couple space.
"""

from uuid import UUID
import structlog

from domain.exceptions import ForbiddenError, NotFoundError
from domain.repositories.photo_repository import PhotoRepository

logger = structlog.get_logger()


class DeletePhotoUseCase:
    """Use case to soft-delete a photo."""

    def __init__(self, photo_repo: PhotoRepository) -> None:
        self.photo_repo = photo_repo

    async def execute(
        self,
        photo_id: UUID,
        user_id: UUID,
        couple_id: UUID,
    ) -> None:
        """Execute the photo deletion.

        Args:
            photo_id: ID of the photo to delete.
            user_id: ID of the user requesting deletion.
            couple_id: ID of the couple space.

        Raises:
            NotFoundError: If photo does not exist.
            ForbiddenError: If photo does not belong to the couple space.
        """
        photo = await self.photo_repo.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")

        # Verify photo belongs to the couple space
        if photo.couple_id != couple_id:
            raise ForbiddenError("You do not have permission to delete this photo")

        # Soft delete the photo
        await self.photo_repo.soft_delete(photo_id)

        logger.info(
            "photo_deleted",
            photo_id=str(photo_id),
            deleted_by=str(user_id),
            couple_id=str(couple_id),
        )
