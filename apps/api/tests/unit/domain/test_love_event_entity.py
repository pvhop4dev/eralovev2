"""Tests for LoveEvent Domain Entity."""

from datetime import date, timedelta
from uuid import uuid4

import pytest

from domain.entities.love_event import LoveEvent
from domain.exceptions import BusinessRuleError


class TestLoveEventEntity:
    """Test suite for LoveEvent entity."""

    def _make_event(self, **overrides) -> LoveEvent:
        defaults = {
            "couple_id": uuid4(),
            "created_by": uuid4(),
            "title": "Valentine's Day 💕",
            "event_type": "date",
            "event_date": date.today() + timedelta(days=10),
        }
        defaults.update(overrides)
        return LoveEvent(**defaults)

    def test_create_event(self):
        event = self._make_event()
        assert event.title == "Valentine's Day 💕"
        assert event.event_type == "date"
        assert event.icon == "❤️"

    def test_auto_icon_date(self):
        event = self._make_event(event_type="date")
        assert event.icon == "❤️"

    def test_auto_icon_anniversary(self):
        event = self._make_event(event_type="anniversary")
        assert event.icon == "💍"

    def test_auto_icon_travel(self):
        event = self._make_event(event_type="travel")
        assert event.icon == "✈️"

    def test_auto_icon_birthday(self):
        event = self._make_event(event_type="birthday")
        assert event.icon == "🎂"

    def test_auto_icon_custom(self):
        event = self._make_event(event_type="custom")
        assert event.icon == "⭐"

    def test_invalid_event_type_raises(self):
        with pytest.raises(BusinessRuleError, match="Invalid event type"):
            self._make_event(event_type="invalid")

    def test_empty_title_raises(self):
        with pytest.raises(BusinessRuleError, match="cannot be empty"):
            self._make_event(title="")

    def test_whitespace_title_raises(self):
        with pytest.raises(BusinessRuleError, match="cannot be empty"):
            self._make_event(title="   ")

    def test_days_until_future(self):
        event = self._make_event(event_date=date.today() + timedelta(days=5))
        assert event.days_until == 5

    def test_days_until_past(self):
        event = self._make_event(event_date=date.today() - timedelta(days=3))
        assert event.days_until == -3

    def test_is_today(self):
        event = self._make_event(event_date=date.today())
        assert event.is_today is True

    def test_is_past(self):
        event = self._make_event(event_date=date.today() - timedelta(days=1))
        assert event.is_past is True

    def test_is_not_past_for_future(self):
        event = self._make_event(event_date=date.today() + timedelta(days=1))
        assert event.is_past is False

    def test_soft_delete(self):
        event = self._make_event()
        event.soft_delete()
        assert event.is_deleted is True
        assert event.deleted_at is not None

    def test_soft_delete_already_deleted_raises(self):
        event = self._make_event()
        event.soft_delete()
        with pytest.raises(BusinessRuleError, match="already deleted"):
            event.soft_delete()

    def test_restore(self):
        event = self._make_event()
        event.soft_delete()
        event.restore()
        assert event.is_deleted is False
        assert event.deleted_at is None

    def test_restore_not_deleted_raises(self):
        event = self._make_event()
        with pytest.raises(BusinessRuleError, match="not deleted"):
            event.restore()

    def test_update_title(self):
        event = self._make_event()
        event.update(title="New Title")
        assert event.title == "New Title"

    def test_update_event_type_changes_icon(self):
        event = self._make_event(event_type="date")
        event.update(event_type="birthday")
        assert event.event_type == "birthday"
        assert event.icon == "🎂"

    def test_update_empty_title_raises(self):
        event = self._make_event()
        with pytest.raises(BusinessRuleError, match="cannot be empty"):
            event.update(title="")

    def test_update_invalid_type_raises(self):
        event = self._make_event()
        with pytest.raises(BusinessRuleError, match="Invalid event type"):
            event.update(event_type="wrong")

    def test_to_dict(self):
        event = self._make_event()
        d = event.to_dict()
        assert d["title"] == "Valentine's Day 💕"
        assert d["event_type"] == "date"
        assert "days_until" in d
        assert d["icon"] == "❤️"

    def test_with_location(self):
        event = self._make_event(location_name="Hồ Gươm, Hà Nội")
        assert event.location_name == "Hồ Gươm, Hà Nội"
