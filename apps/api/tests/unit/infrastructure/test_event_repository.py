"""Unit tests for PostgresLoveEventRepository."""

from datetime import date, time, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from infrastructure.database.models.love_event_model import LoveEventModel
from infrastructure.database.repositories.event_repository import PostgresLoveEventRepository


class TestPostgresLoveEventRepository:
    """Test suite for PostgresLoveEventRepository."""

    @pytest.mark.asyncio
    async def test_get_past_events_on_this_day(self):
        # Arrange
        session = AsyncMock()
        repo = PostgresLoveEventRepository(session)
        couple_id = uuid4()
        user_id = uuid4()
        event_id = uuid4()

        # Mock model instance returned from DB
        mock_model = LoveEventModel(
            id=event_id,
            couple_id=couple_id,
            created_by=user_id,
            title="Kỷ niệm ngày yêu",
            description="Ngày đầu tiên bên nhau",
            event_type="anniversary",
            event_date=date(2025, 5, 31),
            event_time=time(10, 0),
            icon="💍",
            is_recurring=True,
            reminder_before="1 day",
        )

        # Mock execute result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        session.execute.return_value = mock_result

        # Act
        events = await repo.get_past_events_on_this_day(couple_id)

        # Assert
        assert len(events) == 1
        event = events[0]
        assert event.id == event_id
        assert event.couple_id == couple_id
        assert event.title == "Kỷ niệm ngày yêu"
        assert event.event_type == "anniversary"
        assert event.event_date == date(2025, 5, 31)
        assert event.event_time == time(10, 0)
        assert event.icon == "💍"
        assert event.is_recurring is True

        # Check session call
        session.execute.assert_called_once()
        stmt = session.execute.call_args[0][0]
        # Verify columns used in where clauses
        assert "love_events.couple_id = :" in str(stmt)
        assert "extract" in str(stmt).lower()

    @pytest.mark.asyncio
    async def test_get_upcoming(self):
        # Arrange
        session = AsyncMock()
        repo = PostgresLoveEventRepository(session)
        couple_id = uuid4()
        user_id = uuid4()
        event_id = uuid4()

        # Mock model instance
        mock_model = LoveEventModel(
            id=event_id,
            couple_id=couple_id,
            created_by=user_id,
            title="Đi du lịch Đà Lạt",
            description="Chuyến đi 3 ngày 2 đêm",
            event_type="travel",
            event_date=date.today() + timedelta(days=2),
            event_time=time(8, 0),
            icon="✈️",
            is_recurring=False,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_model]
        session.execute.return_value = mock_result

        # Act
        events = await repo.get_upcoming(couple_id, days=7)

        # Assert
        assert len(events) == 1
        event = events[0]
        assert event.id == event_id
        assert event.couple_id == couple_id
        assert event.title == "Đi du lịch Đà Lạt"
        assert event.event_type == "travel"
        assert event.icon == "✈️"
        assert event.is_recurring is False

        # Check session call
        session.execute.assert_called_once()
        stmt = session.execute.call_args[0][0]
        assert "love_events.couple_id = :" in str(stmt)
        assert "love_events.event_date >=" in str(stmt)
        assert "love_events.event_date <=" in str(stmt)
