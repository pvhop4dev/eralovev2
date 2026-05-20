"""Tests for DeclineMatchRequest Use Case."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.use_cases.match.decline_request import DeclineMatchRequestUseCase
from domain.entities.match_request import MatchRequest
from domain.exceptions import ForbiddenError, NotFoundError


class TestDeclineMatchRequestUseCase:
    """Test suite for DeclineMatchRequest use case."""

    def setup_method(self):
        self.match_repo = AsyncMock()
        self.uc = DeclineMatchRequestUseCase(self.match_repo)
        self.sender_id = uuid4()
        self.receiver_id = uuid4()

    @pytest.mark.asyncio
    async def test_decline_success(self):
        req = MatchRequest(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
        )
        self.match_repo.get_by_id.return_value = req

        await self.uc.execute(self.receiver_id, req.id)

        self.match_repo.update.assert_called_once()
        assert req.status == "declined"

    @pytest.mark.asyncio
    async def test_decline_not_found_raises(self):
        self.match_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await self.uc.execute(self.receiver_id, uuid4())

    @pytest.mark.asyncio
    async def test_decline_by_sender_raises_forbidden(self):
        req = MatchRequest(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
        )
        self.match_repo.get_by_id.return_value = req
        with pytest.raises(ForbiddenError, match="Only the receiver"):
            await self.uc.execute(self.sender_id, req.id)

    @pytest.mark.asyncio
    async def test_decline_by_third_party_raises_forbidden(self):
        req = MatchRequest(
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
        )
        self.match_repo.get_by_id.return_value = req
        third_party = uuid4()
        with pytest.raises(ForbiddenError):
            await self.uc.execute(third_party, req.id)
