"""Match Request Domain Entity.

Represents a request from one user to match with another.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleError


@dataclass
class MatchRequest:
    """MatchRequest entity — a pending match invitation."""

    sender_id: UUID
    receiver_id: UUID
    id: UUID = field(default_factory=uuid4)
    message: str | None = None
    status: str = "pending"  # pending, accepted, declined, expired
    proposed_start_date: date | None = None
    expires_at: datetime | None = None
    responded_at: datetime | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        """Set default expiry (7 days) if not provided."""
        if self.expires_at is None:
            self.expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    @property
    def is_pending(self) -> bool:
        """Check if request is still pending."""
        return self.status == "pending" and not self.is_expired

    @property
    def is_expired(self) -> bool:
        """Check if request has expired."""
        if self.status == "expired":
            return True
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return True
        return False

    def accept(self, start_date: date | None = None) -> None:
        """Accept the match request.

        Args:
            start_date: The couple's start date (defaults to today).

        Raises:
            BusinessRuleError: If not pending or expired.
        """
        if self.status != "pending":
            raise BusinessRuleError(f"Cannot accept — status is '{self.status}'")
        if self.is_expired:
            self.status = "expired"
            raise BusinessRuleError("Match request has expired")

        self.status = "accepted"
        self.responded_at = datetime.now(timezone.utc)
        if start_date:
            self.proposed_start_date = start_date

    def decline(self) -> None:
        """Decline the match request.

        Raises:
            BusinessRuleError: If not pending.
        """
        if self.status != "pending":
            raise BusinessRuleError(f"Cannot decline — status is '{self.status}'")

        self.status = "declined"
        self.responded_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        """Mark the request as expired."""
        if self.status == "pending":
            self.status = "expired"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "message": self.message,
            "status": self.status,
            "proposed_start_date": self.proposed_start_date.isoformat() if self.proposed_start_date else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
