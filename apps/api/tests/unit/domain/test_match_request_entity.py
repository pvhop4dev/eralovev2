"""Tests for MatchRequest Domain Entity."""

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from domain.entities.match_request import MatchRequest
from domain.exceptions import BusinessRuleError


class TestMatchRequestEntity:
    """Test suite for MatchRequest entity."""

    def _make_request(self, **overrides) -> MatchRequest:
        defaults = {
            "sender_id": uuid4(),
            "receiver_id": uuid4(),
        }
        defaults.update(overrides)
        return MatchRequest(**defaults)

    def test_create_request(self):
        req = self._make_request()
        assert req.status == "pending"
        assert req.is_pending is True
        assert req.expires_at is not None

    def test_default_expiry_is_7_days(self):
        req = self._make_request()
        now = datetime.now(UTC)
        # Should be roughly 7 days from now
        diff = req.expires_at - now
        assert 6 <= diff.days <= 7

    def test_accept(self):
        req = self._make_request()
        req.accept(start_date=date.today())
        assert req.status == "accepted"
        assert req.responded_at is not None
        assert req.proposed_start_date == date.today()

    def test_accept_already_accepted_raises(self):
        req = self._make_request()
        req.accept()
        with pytest.raises(BusinessRuleError, match="Cannot accept"):
            req.accept()

    def test_accept_expired_raises(self):
        req = self._make_request(
            expires_at=datetime.now(UTC) - timedelta(hours=1)
        )
        with pytest.raises(BusinessRuleError, match="expired"):
            req.accept()

    def test_decline(self):
        req = self._make_request()
        req.decline()
        assert req.status == "declined"
        assert req.responded_at is not None

    def test_decline_already_declined_raises(self):
        req = self._make_request()
        req.decline()
        with pytest.raises(BusinessRuleError, match="Cannot decline"):
            req.decline()

    def test_is_expired(self):
        req = self._make_request(
            expires_at=datetime.now(UTC) - timedelta(hours=1)
        )
        assert req.is_expired is True
        assert req.is_pending is False

    def test_not_expired(self):
        req = self._make_request()
        assert req.is_expired is False
        assert req.is_pending is True

    def test_expire(self):
        req = self._make_request()
        req.expire()
        assert req.status == "expired"

    def test_to_dict(self):
        req = self._make_request(message="Hey! 💕")
        d = req.to_dict()
        assert d["message"] == "Hey! 💕"
        assert d["status"] == "pending"

    def test_custom_message(self):
        req = self._make_request(message="Mình ghép đôi nhé! 💗")
        assert req.message == "Mình ghép đôi nhé! 💗"

    def test_proposed_start_date(self):
        d = date(2024, 2, 14)
        req = self._make_request(proposed_start_date=d)
        assert req.proposed_start_date == d
