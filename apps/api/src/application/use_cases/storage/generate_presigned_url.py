"""Generate Presigned URL Use Case."""

import mimetypes
import os
import uuid

import structlog

from application.dtos.storage_dto import PresignedUrlRequest, PresignedUrlResponse
from domain.exceptions import ValidationError
from infrastructure.storage.s3_service import S3Service

logger = structlog.get_logger()

# Allowed image MIME types for profile avatars and couple events
_ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}

# Ensure standard image mime types are registered, especially for older Python versions
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/gif", ".gif")


class GeneratePresignedUrlUseCase:
    """Generate a secure S3 presigned upload URL for direct file upload."""

    def __init__(self, s3_service: S3Service) -> None:
        self.s3_service = s3_service

    async def execute(self, dto: PresignedUrlRequest) -> PresignedUrlResponse:
        """Validate request and generate presigned URL.

        Args:
            dto: The PresignedUrlRequest data.

        Returns:
            PresignedUrlResponse containing the upload and access URLs.
        """
        content_type = dto.content_type.lower()
        if content_type not in _ALLOWED_IMAGE_TYPES:
            logger.warning("invalid_file_type_rejected", content_type=content_type)
            raise ValidationError(
                f"File type '{content_type}' is not allowed. Only images are permitted."
            )

        # Get file extension from file name or fallback to mimetype
        _, ext = os.path.splitext(dto.file_name.lower())
        if not ext:
            ext = mimetypes.guess_extension(content_type) or ".jpg"

        # Construct key path (e.g. avatars/{uuid}.png or events/{uuid}.jpg)
        unique_id = uuid.uuid4()
        folder = "avatars" if dto.file_type == "avatar" else "events"
        key = f"{folder}/{unique_id}{ext}"

        # Generate URLs
        urls = self.s3_service.generate_presigned_upload_url(key=key, content_type=content_type)

        return PresignedUrlResponse(
            upload_url=urls["upload_url"],
            file_url=urls["file_url"],
        )
