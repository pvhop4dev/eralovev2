"""Tests for SendMatchRequest Use Case."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.dtos.match_dto import SendMatchRequestDTO
from application.use_cases.match.send_request import SendMatchRequestUseCase
from domain.entities.couple import Couple
from domain.entities.user import User
from domain.exceptions import AlreadyMatchedError, BusinessRuleError, ConflictError, UserNotFoundError


class TestSendMatchRequestUseCase:
    """Test suite for SendMatchRequestUseCase."""

    def _make_user(self, **overrides) -> User:
        defaults = {
            "id": uuid4(),
            "email": "test@example.com",
            "display_name": "Test",
            "username": "test",
        }
        defaults.update(overrides)
        return User(**defaults)

    @pytest.mark.asyncio
    async def test_send_success(self):
        sender = self._make_user()
        receiver = self._make_user(id=uuid4(), email="r@e.com", username="recv")

        user_repo = AsyncMock()
        user_repo.get_by_id.side_effect = lambda uid: receiver if uid == receiver.id else sender
        match_repo = AsyncMock()
        match_repo.get_pending_between.return_value = None
        match_repo.create.side_effect = lambda req: req
        couple_repo = AsyncMock()
        couple_repo.get_active_for_user.return_value = None

        uc = SendMatchRequestUseCase(user_repo, match_repo, couple_repo)
        dto = SendMatchRequestDTO(receiver_id=str(receiver.id), message="Hey!")

        result = await uc.execute(sender.id, dto)
        assert result.status == "pending"
        assert result.receiver_name == "Test"
        match_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_self_match_raises(self):
        user_id = uuid4()
        uc = SendMatchRequestUseCase(AsyncMock(), AsyncMock(), AsyncMock())
        dto = SendMatchRequestDTO(receiver_id=str(user_id))

        with pytest.raises(BusinessRuleError, match="yourself"):
            await uc.execute(user_id, dto)

    @pytest.mark.asyncio
    async def test_receiver_not_found_raises(self):
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = None
        couple_repo = AsyncMock()
        couple_repo.get_active_for_user.return_value = None

        uc = SendMatchRequestUseCase(user_repo, AsyncMock(), couple_repo)
        dto = SendMatchRequestDTO(receiver_id=str(uuid4()))

        with pytest.raises(UserNotFoundError):
            await uc.execute(uuid4(), dto)

    @pytest.mark.asyncio
    async def test_sender_already_matched_raises(self):
        sender_id = uuid4()
        receiver = self._make_user()

        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = receiver
        couple_repo = AsyncMock()
        couple_repo.get_active_for_user.side_effect = lambda uid: (
            Couple(user1_id=sender_id, user2_id=uuid4(), start_date=__import__("datetime").date.today())
            if uid == sender_id
            else None
        )

        uc = SendMatchRequestUseCase(user_repo, AsyncMock(), couple_repo)
        dto = SendMatchRequestDTO(receiver_id=str(receiver.id))

        with pytest.raises(AlreadyMatchedError):
            await uc.execute(sender_id, dto)

    @pytest.mark.asyncio
    async def test_duplicate_pending_raises(self):
        sender_id = uuid4()
        receiver = self._make_user()

        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = receiver
        match_repo = AsyncMock()
        match_repo.get_pending_between.side_effect = lambda s, r: (
            "existing" if s == sender_id else None
        )
        couple_repo = AsyncMock()
        couple_repo.get_active_for_user.return_value = None

        uc = SendMatchRequestUseCase(user_repo, match_repo, couple_repo)
        dto = SendMatchRequestDTO(receiver_id=str(receiver.id))

        with pytest.raises(ConflictError, match="pending"):
            await uc.execute(sender_id, dto)
