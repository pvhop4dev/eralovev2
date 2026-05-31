"""Unit tests for Photo Use Cases."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.dtos.photo_dto import AddPhotoRequest
from application.use_cases.photo.add_photo import AddPhotoUseCase
from application.use_cases.photo.delete_photo import DeletePhotoUseCase
from domain.entities.love_event import LoveEvent
from domain.entities.photo import Photo
from domain.exceptions import ForbiddenError, NotFoundError


class TestPhotoUseCases:
    """Test suite for Photo use cases."""

    @pytest.mark.asyncio
    async def test_add_photo_without_event_success(self):
        # Arrange
        photo_repo = AsyncMock()
        event_repo = AsyncMock()
        use_case = AddPhotoUseCase(photo_repo, event_repo)

        couple_id = uuid4()
        user_id = uuid4()
        
        request = AddPhotoRequest(
            s3_key="events/photo.jpg",
            original_url="http://localhost:9000/eralove-media/events/photo.jpg",
            caption="Cute couple",
        )

        mock_created_photo = Photo(
            id=uuid4(),
            couple_id=couple_id,
            uploaded_by=user_id,
            s3_key=request.s3_key,
            original_url=request.original_url,
            caption=request.caption,
        )
        photo_repo.create.return_value = mock_created_photo

        # Act
        response = await use_case.execute(request, user_id, couple_id)

        # Assert
        assert response.s3_key == request.s3_key
        assert response.original_url == request.original_url
        assert response.caption == "Cute couple"
        photo_repo.create.assert_called_once()
        event_repo.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_photo_with_event_success(self):
        # Arrange
        photo_repo = AsyncMock()
        event_repo = AsyncMock()
        use_case = AddPhotoUseCase(photo_repo, event_repo)

        couple_id = uuid4()
        user_id = uuid4()
        event_id = uuid4()
        
        request = AddPhotoRequest(
            s3_key="events/photo.jpg",
            original_url="http://localhost:9000/eralove-media/events/photo.jpg",
            event_id=str(event_id),
        )

        mock_event = MagicMock(spec=LoveEvent)
        mock_event.couple_id = couple_id
        event_repo.get_by_id.return_value = mock_event

        mock_created_photo = Photo(
            id=uuid4(),
            couple_id=couple_id,
            uploaded_by=user_id,
            event_id=event_id,
            s3_key=request.s3_key,
            original_url=request.original_url,
        )
        photo_repo.create.return_value = mock_created_photo

        # Act
        response = await use_case.execute(request, user_id, couple_id)

        # Assert
        assert response.event_id == str(event_id)
        event_repo.get_by_id.assert_called_once_with(event_id)
        photo_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_photo_event_not_found_raises(self):
        # Arrange
        photo_repo = AsyncMock()
        event_repo = AsyncMock()
        use_case = AddPhotoUseCase(photo_repo, event_repo)

        couple_id = uuid4()
        user_id = uuid4()
        event_id = uuid4()
        
        request = AddPhotoRequest(
            s3_key="events/photo.jpg",
            original_url="http://localhost:9000/eralove-media/events/photo.jpg",
            event_id=str(event_id),
        )

        event_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError, match="Calendar event not found"):
            await use_case.execute(request, user_id, couple_id)

        photo_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_photo_event_other_couple_raises(self):
        # Arrange
        photo_repo = AsyncMock()
        event_repo = AsyncMock()
        use_case = AddPhotoUseCase(photo_repo, event_repo)

        couple_id = uuid4()
        other_couple_id = uuid4()
        user_id = uuid4()
        event_id = uuid4()
        
        request = AddPhotoRequest(
            s3_key="events/photo.jpg",
            original_url="http://localhost:9000/eralove-media/events/photo.jpg",
            event_id=str(event_id),
        )

        mock_event = MagicMock(spec=LoveEvent)
        mock_event.couple_id = other_couple_id
        event_repo.get_by_id.return_value = mock_event

        # Act & Assert
        with pytest.raises(ForbiddenError, match="does not belong to your couple space"):
            await use_case.execute(request, user_id, couple_id)

        photo_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_photo_success(self):
        # Arrange
        photo_repo = AsyncMock()
        use_case = DeletePhotoUseCase(photo_repo)

        couple_id = uuid4()
        user_id = uuid4()
        photo_id = uuid4()

        mock_photo = MagicMock(spec=Photo)
        mock_photo.couple_id = couple_id
        photo_repo.get_by_id.return_value = mock_photo

        # Act
        await use_case.execute(photo_id, user_id, couple_id)

        # Assert
        photo_repo.get_by_id.assert_called_once_with(photo_id)
        photo_repo.soft_delete.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_delete_photo_not_found_raises(self):
        # Arrange
        photo_repo = AsyncMock()
        use_case = DeletePhotoUseCase(photo_repo)

        couple_id = uuid4()
        user_id = uuid4()
        photo_id = uuid4()

        photo_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError, match="Photo not found"):
            await use_case.execute(photo_id, user_id, couple_id)

        photo_repo.soft_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_photo_forbidden_raises(self):
        # Arrange
        photo_repo = AsyncMock()
        use_case = DeletePhotoUseCase(photo_repo)

        couple_id = uuid4()
        other_couple_id = uuid4()
        user_id = uuid4()
        photo_id = uuid4()

        mock_photo = MagicMock(spec=Photo)
        mock_photo.couple_id = other_couple_id
        photo_repo.get_by_id.return_value = mock_photo

        # Act & Assert
        with pytest.raises(ForbiddenError, match="permission to delete this photo"):
            await use_case.execute(photo_id, user_id, couple_id)

        photo_repo.soft_delete.assert_not_called()
