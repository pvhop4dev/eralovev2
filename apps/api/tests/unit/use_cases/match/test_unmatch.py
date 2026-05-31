"""Tests for Unmatch Use Case."""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.use_cases.match.unmatch import UnmatchUseCase
from domain.entities.couple import Couple
from domain.exceptions import BusinessRuleError, CoupleNotFoundError


class TestUnmatchUseCase:
    """Test suite for UnmatchUseCase."""

    def setup_method(self):
        self.couple_repo = AsyncMock()
        self.use_case = UnmatchUseCase(self.couple_repo)
        self.user_id = uuid4()
        self.partner_id = uuid4()

    @pytest.mark.asyncio
    async def test_unmatch_success(self):
        # Create an active couple
        couple = Couple(
            user1_id=self.user_id,
            user2_id=self.partner_id,
            start_date=date(2026, 1, 1),
            status="active",
        )
        self.couple_repo.get_active_for_user.return_value = couple
        self.couple_repo.update.return_value = couple

        await self.use_case.execute(self.user_id)

        # Verify that the couple status changed and repo.update was called
        assert couple.status == "broken_up"
        assert couple.broken_up_at is not None
        self.couple_repo.update.assert_called_once_with(couple)

    @pytest.mark.asyncio
    async def test_unmatch_no_active_couple_raises(self):
        # No active couple for this user
        self.couple_repo.get_active_for_user.return_value = None

        with pytest.raises(CoupleNotFoundError):
            await self.use_case.execute(self.user_id)

        self.couple_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_couple_break_up_already_broken_up_raises(self):
        # Create an already broken up couple
        couple = Couple(
            user1_id=self.user_id,
            user2_id=self.partner_id,
            start_date=date(2026, 1, 1),
            status="broken_up",
        )
        
        with pytest.raises(BusinessRuleError, match="Already broken up"):
            couple.break_up()
