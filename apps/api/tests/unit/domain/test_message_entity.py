"""Tests for Message Domain Entity."""

from uuid import uuid4

import pytest

from domain.entities.message import Message
from domain.exceptions import BusinessRuleError


class TestMessageEntity:
    """Test suite for Message entity."""

    def _make_msg(self, **overrides) -> Message:
        defaults = {
            "couple_id": uuid4(),
            "sender_id": uuid4(),
            "content": "Anh yêu em 💕",
            "message_type": "text",
        }
        defaults.update(overrides)
        return Message(**defaults)

    def test_create_text_message(self):
        msg = self._make_msg()
        assert msg.content == "Anh yêu em 💕"
        assert msg.message_type == "text"
        assert msg.status == "sent"

    def test_text_without_content_raises(self):
        with pytest.raises(BusinessRuleError, match="must have content"):
            self._make_msg(content=None)

    def test_image_without_media_raises(self):
        with pytest.raises(BusinessRuleError, match="must have media_url"):
            self._make_msg(message_type="image", content=None, media_url=None)

    def test_image_with_media_ok(self):
        msg = self._make_msg(
            message_type="image", content=None, media_url="https://s3/photo.jpg"
        )
        assert msg.message_type == "image"
        assert msg.media_url == "https://s3/photo.jpg"

    def test_voice_with_media_ok(self):
        msg = self._make_msg(
            message_type="voice", content=None, media_url="https://s3/voice.ogg"
        )
        assert msg.message_type == "voice"

    def test_love_message(self):
        msg = self._make_msg(message_type="love_message")
        assert msg.message_type == "love_message"

    def test_invalid_type_raises(self):
        with pytest.raises(BusinessRuleError, match="Invalid message type"):
            self._make_msg(message_type="sticker")

    def test_mark_delivered(self):
        msg = self._make_msg()
        msg.mark_delivered()
        assert msg.status == "delivered"
        assert msg.delivered_at is not None

    def test_mark_delivered_only_from_sent(self):
        msg = self._make_msg()
        msg.mark_read()  # skip to read
        msg.mark_delivered()  # no-op when already read
        assert msg.status == "read"

    def test_mark_read(self):
        msg = self._make_msg()
        msg.mark_read()
        assert msg.status == "read"
        assert msg.read_at is not None
        assert msg.delivered_at is not None

    def test_mark_read_from_delivered(self):
        msg = self._make_msg()
        msg.mark_delivered()
        msg.mark_read()
        assert msg.status == "read"

    def test_pin_unpin(self):
        msg = self._make_msg()
        assert msg.is_pinned is False
        msg.pin()
        assert msg.is_pinned is True
        msg.unpin()
        assert msg.is_pinned is False

    def test_soft_delete(self):
        msg = self._make_msg()
        msg.soft_delete()
        assert msg.is_deleted is True

    def test_double_delete_raises(self):
        msg = self._make_msg()
        msg.soft_delete()
        with pytest.raises(BusinessRuleError, match="already deleted"):
            msg.soft_delete()

    def test_to_dict(self):
        msg = self._make_msg()
        d = msg.to_dict()
        assert d["content"] == "Anh yêu em 💕"
        assert d["message_type"] == "text"
        assert d["status"] == "sent"
        assert d["is_pinned"] is False

    def test_reply_to(self):
        original = uuid4()
        msg = self._make_msg(reply_to_id=original)
        assert msg.reply_to_id == original
        d = msg.to_dict()
        assert d["reply_to_id"] == str(original)
