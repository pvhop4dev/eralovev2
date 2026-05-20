"""Tests for Couple Domain Entity."""

from datetime import date, timedelta
from uuid import uuid4

import pytest

from domain.entities.couple import Couple
from domain.exceptions import BusinessRuleError


class TestCoupleEntity:
    """Test suite for Couple entity."""

    def _make_couple(self, **overrides) -> Couple:
        defaults = {
            "user1_id": uuid4(),
            "user2_id": uuid4(),
            "start_date": date.today() - timedelta(days=100),
        }
        defaults.update(overrides)
        return Couple(**defaults)

    def test_create_couple(self):
        couple = self._make_couple()
        assert couple.status == "active"
        assert couple.theme_color == "rose"
        assert couple.is_active is True

    def test_days_together(self):
        couple = self._make_couple(start_date=date.today() - timedelta(days=50))
        assert couple.days_together == 50

    def test_days_together_today(self):
        couple = self._make_couple(start_date=date.today())
        assert couple.days_together == 0

    def test_has_user(self):
        u1, u2, u3 = uuid4(), uuid4(), uuid4()
        couple = self._make_couple(user1_id=u1, user2_id=u2)
        assert couple.has_user(u1) is True
        assert couple.has_user(u2) is True
        assert couple.has_user(u3) is False

    def test_get_partner_id(self):
        u1, u2 = uuid4(), uuid4()
        couple = self._make_couple(user1_id=u1, user2_id=u2)
        assert couple.get_partner_id(u1) == u2
        assert couple.get_partner_id(u2) == u1

    def test_get_partner_id_not_in_couple_raises(self):
        couple = self._make_couple()
        with pytest.raises(BusinessRuleError, match="not part of"):
            couple.get_partner_id(uuid4())

    def test_pause(self):
        couple = self._make_couple()
        couple.pause()
        assert couple.status == "paused"
        assert couple.is_paused is True
        assert couple.paused_at is not None

    def test_pause_already_paused_raises(self):
        couple = self._make_couple()
        couple.pause()
        with pytest.raises(BusinessRuleError, match="Cannot pause"):
            couple.pause()

    def test_resume(self):
        couple = self._make_couple()
        couple.pause()
        couple.resume()
        assert couple.status == "active"
        assert couple.paused_at is None

    def test_resume_not_paused_raises(self):
        couple = self._make_couple()
        with pytest.raises(BusinessRuleError, match="not paused"):
            couple.resume()

    def test_break_up(self):
        couple = self._make_couple()
        couple.break_up()
        assert couple.status == "broken_up"
        assert couple.broken_up_at is not None
        assert couple.is_active is False

    def test_break_up_already_broken_raises(self):
        couple = self._make_couple()
        couple.break_up()
        with pytest.raises(BusinessRuleError, match="Already broken up"):
            couple.break_up()

    def test_update_settings(self):
        couple = self._make_couple()
        couple.update_settings(
            theme_color="lavender",
            nicknames={"user1": "Gấu", "user2": "Mèo"},
        )
        assert couple.theme_color == "lavender"
        assert couple.nicknames == {"user1": "Gấu", "user2": "Mèo"}

    def test_to_dict(self):
        couple = self._make_couple()
        d = couple.to_dict()
        assert "id" in d
        assert "days_together" in d
        assert d["status"] == "active"
