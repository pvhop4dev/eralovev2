"""Unit tests for PostgresPhotoRepository."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from infrastructure.database.models.photo_model import PhotoModel
from infrastructure.database.repositories.photo_repository import PostgresPhotoRepository


class TestPostgresPhotoRepository:
    """Test suite for PostgresPhotoRepository."""

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        # Arrange
        session = AsyncMock()
        repo = PostgresPhotoRepository(session)
        photo_id = uuid4()
        couple_id = uuid4()
        user_id = uuid4()

        mock_model = PhotoModel(
            id=photo_id,
            couple_id=couple_id,
            uploaded_by=user_id,
            s3_key="events/img.jpg",
            original_url="http://localhost:9000/eralove-media/events/img.jpg",
            caption="Lovely moment",
            photo_date=date(2025, 5, 20),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        session.execute.return_value = mock_result

        # Act
        photo = await repo.get_by_id(photo_id)

        # Assert
        assert photo is not None
        assert photo.id == photo_id
        assert photo.caption == "Lovely moment"
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_couple(self):
        # Arrange
        session = AsyncMock()
        repo = PostgresPhotoRepository(session)
        couple_id = uuid4()
        photo_id = uuid4()

        mock_model = PhotoModel(
            id=photo_id,
            couple_id=couple_id,
            uploaded_by=uuid4(),
            s3_key="events/img.jpg",
            original_url="http://localhost:9000/eralove-media/events/img.jpg",
            photo_date=date(2025, 5, 20),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        session.execute.return_value = mock_result

        # Act
        photos = await repo.get_by_couple(couple_id)

        # Assert
        assert len(photos) == 1
        assert photos[0].id == photo_id
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_event(self):
        # Arrange
        session = AsyncMock()
        repo = PostgresPhotoRepository(session)
        event_id = uuid4()
        photo_id = uuid4()

        mock_model = PhotoModel(
            id=photo_id,
            couple_id=uuid4(),
            uploaded_by=uuid4(),
            event_id=event_id,
            s3_key="events/img.jpg",
            original_url="http://localhost:9000/eralove-media/events/img.jpg",
            photo_date=date(2025, 5, 20),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        session.execute.return_value = mock_result

        # Act
        photos = await repo.get_by_event(event_id)

        # Assert
        assert len(photos) == 1
        assert photos[0].event_id == event_id
        session.execute.assert_called_once()
