"""Tests for Generate Presigned URL Use Case."""

from unittest.mock import MagicMock

import pytest

from application.dtos.storage_dto import PresignedUrlRequest
from application.use_cases.storage.generate_presigned_url import GeneratePresignedUrlUseCase
from domain.exceptions import ValidationError


class TestGeneratePresignedUrlUseCase:
    """Test suite for GeneratePresignedUrlUseCase."""

    @pytest.mark.asyncio
    async def test_generate_avatar_presigned_url_success(self):
        s3_service = MagicMock()
        s3_service.generate_presigned_upload_url.return_value = {
            "upload_url": "https://s3.example.com/upload/avatars/123.png",
            "file_url": "https://s3.example.com/files/avatars/123.png",
        }

        use_case = GeneratePresignedUrlUseCase(s3_service=s3_service)
        dto = PresignedUrlRequest(
            file_name="me.png",
            content_type="image/png",
            file_type="avatar",
        )

        response = await use_case.execute(dto)

        assert response.upload_url == "https://s3.example.com/upload/avatars/123.png"
        assert response.file_url == "https://s3.example.com/files/avatars/123.png"

        # Verify s3_service called with correct prefix and type
        called_args = s3_service.generate_presigned_upload_url.call_args[1]
        assert called_args["content_type"] == "image/png"
        assert called_args["key"].startswith("avatars/")
        assert called_args["key"].endswith(".png")

    @pytest.mark.asyncio
    async def test_generate_event_presigned_url_success(self):
        s3_service = MagicMock()
        s3_service.generate_presigned_upload_url.return_value = {
            "upload_url": "https://s3.example.com/upload/events/123.jpg",
            "file_url": "https://s3.example.com/files/events/123.jpg",
        }

        use_case = GeneratePresignedUrlUseCase(s3_service=s3_service)
        dto = PresignedUrlRequest(
            file_name="date.JPG",
            content_type="image/jpeg",
            file_type="event",
        )

        response = await use_case.execute(dto)

        assert response.upload_url == "https://s3.example.com/upload/events/123.jpg"
        assert response.file_url == "https://s3.example.com/files/events/123.jpg"

        called_args = s3_service.generate_presigned_upload_url.call_args[1]
        assert called_args["content_type"] == "image/jpeg"
        assert called_args["key"].startswith("events/")
        assert called_args["key"].endswith(".jpg")

    @pytest.mark.asyncio
    async def test_generate_presigned_url_invalid_mime_raises_validation_error(self):
        s3_service = MagicMock()
        use_case = GeneratePresignedUrlUseCase(s3_service=s3_service)

        dto = PresignedUrlRequest(
            file_name="exploit.exe",
            content_type="application/octet-stream",
            file_type="avatar",
        )

        with pytest.raises(ValidationError) as exc_info:
            await use_case.execute(dto)

        assert "Only images are permitted" in str(exc_info.value)
        s3_service.generate_presigned_upload_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_presigned_url_fallback_extension(self):
        s3_service = MagicMock()
        s3_service.generate_presigned_upload_url.return_value = {
            "upload_url": "https://s3.example.com/upload/avatars/123.webp",
            "file_url": "https://s3.example.com/files/avatars/123.webp",
        }

        use_case = GeneratePresignedUrlUseCase(s3_service=s3_service)
        # file_name has no extension
        dto = PresignedUrlRequest(
            file_name="profile-no-extension",
            content_type="image/webp",
            file_type="avatar",
        )

        await use_case.execute(dto)

        called_args = s3_service.generate_presigned_upload_url.call_args[1]
        assert called_args["content_type"] == "image/webp"
        assert called_args["key"].startswith("avatars/")
        assert called_args["key"].endswith(".webp")  # Guessed from image/webp
