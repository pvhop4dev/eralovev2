"""Message Domain Entity.

Represents a chat message between a couple.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleError

MESSAGE_TYPES = {"text", "image", "voice", "love_message"}
MESSAGE_STATUSES = {"sent", "delivered", "read"}


@dataclass
class Message:
    """Message entity — a single chat message."""

    couple_id: UUID
    sender_id: UUID
    id: UUID = field(default_factory=uuid4)
    content: str | None = None
    message_type: str = "text"
    media_url: str | None = None
    media_metadata: dict | None = None
    reply_to_id: UUID | None = None
    is_pinned: bool = False
    status: str = "sent"  # sent, delivered, read
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate message type and content."""
        if self.message_type not in MESSAGE_TYPES:
            raise BusinessRuleError(
                f"Invalid message type '{self.message_type}'. Must be one of: {', '.join(MESSAGE_TYPES)}"
            )
        if self.message_type == "text" and not self.content:
            raise BusinessRuleError("Text message must have content")
        if self.message_type in ("image", "voice") and not self.media_url:
            raise BusinessRuleError(f"{self.message_type} message must have media_url")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def mark_delivered(self) -> None:
        """Mark message as delivered."""
        if self.status == "sent":
            self.status = "delivered"
            self.delivered_at = datetime.now(UTC)

    def mark_read(self) -> None:
        """Mark message as read."""
        if self.status in ("sent", "delivered"):
            self.status = "read"
            self.read_at = datetime.now(UTC)
            if not self.delivered_at:
                self.delivered_at = self.read_at

    def pin(self) -> None:
        """Pin the message."""
        self.is_pinned = True

    def unpin(self) -> None:
        """Unpin the message."""
        self.is_pinned = False

    def soft_delete(self) -> None:
        """Soft delete the message."""
        if self.is_deleted:
            raise BusinessRuleError("Message is already deleted")
        self.deleted_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "couple_id": str(self.couple_id),
            "sender_id": str(self.sender_id),
            "content": self.content,
            "message_type": self.message_type,
            "media_url": self.media_url,
            "reply_to_id": str(self.reply_to_id) if self.reply_to_id else None,
            "is_pinned": self.is_pinned,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
