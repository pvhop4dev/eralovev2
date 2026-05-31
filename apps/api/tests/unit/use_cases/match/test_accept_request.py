"""Tests for AcceptMatchRequest Use Case."""

from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from application.dtos.match_dto import AcceptMatchRequestDTO
from application.use_cases.match.accept_request import AcceptMatchRequestUseCase
from domain.entities.match_request import MatchRequest
from domain.exceptions import BusinessRuleError, ForbiddenError, NotFoundError


class TestAcceptMatchRequestUseCase:
    """Test suite for AcceptMatchRequest use case."""

    def setup_method(self):
        self.match_repo = AsyncMock()
        self.couple_repo = AsyncMock()
        self.uc = AcceptMatchRequestUseCase(self.match_repo, self.couple_repo)
        self.sender_id = uuid4()
        self.receiver_id = uuid4()

    def _make_request(self, **overrides) -> MatchRequest:
        defaults = {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "status": "pending",
        }
        defaults.update(overrides)
        return MatchRequest(**defaults)

    @pytest.mark.asyncio
    async def test_accept_success(self):
        req = self._make_request()
        self.match_repo.get_by_id.return_value = req
        self.couple_repo.create.return_value = MagicMock(
            id=uuid4(), user1_id=self.sender_id, user2_id=self.receiver_id,
            start_date=date.today(), status="active", theme_color="rose",
            days_together=0,
        )
        dto = AcceptMatchRequestDTO(start_date=date.today())
        result = await self.uc.execute(self.receiver_id, req.id, dto)

        assert result.status == "active"
        self.match_repo.update.assert_called_once()
        self.couple_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_not_found_raises(self):
        self.match_repo.get_by_id.return_value = None
        dto = AcceptMatchRequestDTO(start_date=date.today())
        with pytest.raises(NotFoundError):
            await self.uc.execute(self.receiver_id, uuid4(), dto)

    @pytest.mark.asyncio
    async def test_accept_by_sender_raises_forbidden(self):
        req = self._make_request()
        self.match_repo.get_by_id.return_value = req
        dto = AcceptMatchRequestDTO(start_date=date.today())
        with pytest.raises(ForbiddenError, match="Only the receiver"):
            await self.uc.execute(self.sender_id, req.id, dto)

    @pytest.mark.asyncio
    async def test_accept_expired_raises(self):
        req = MatchRequest(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.match_repo.get_by_id.return_value = req
        dto = AcceptMatchRequestDTO(start_date=date.today())
        with pytest.raises(BusinessRuleError):
            await self.uc.execute(self.receiver_id, req.id, dto)
