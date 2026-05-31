"""LoveEvent Domain Entity.

Represents calendar events for a couple — dates, anniversaries,
birthdays, travel, and custom events.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleError

# Valid event types
EVENT_TYPES = {"date", "anniversary", "travel", "birthday", "custom"}

# Event type icons mapping
EVENT_ICONS = {
    "date": "❤️",
    "anniversary": "💍",
    "travel": "✈️",
    "birthday": "🎂",
    "custom": "⭐",
}


@dataclass
class LoveEvent:
    """LoveEvent domain entity — a calendar event for a couple."""

    couple_id: UUID
    created_by: UUID
    title: str
    event_type: str
    event_date: date
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    event_time: time | None = None
    end_date: date | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    color: str | None = None
    icon: str | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None
    reminder_before: str | None = None  # e.g., "1 day", "1 week"
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate event type and set default icon."""
        if self.event_type not in EVENT_TYPES:
            raise BusinessRuleError(
                f"Invalid event type '{self.event_type}'. Must be one of: {', '.join(EVENT_TYPES)}"
            )
        if not self.icon:
            self.icon = EVENT_ICONS.get(self.event_type, "⭐")
        if not self.title.strip():
            raise BusinessRuleError("Event title cannot be empty")

    @property
    def is_deleted(self) -> bool:
        """Check if event is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_past(self) -> bool:
        """Check if event date has passed."""
        return self.event_date < date.today()

    @property
    def is_today(self) -> bool:
        """Check if event is today."""
        return self.event_date == date.today()

    @property
    def days_until(self) -> int:
        """Days until the event (negative if past)."""
        return (self.event_date - date.today()).days

    def soft_delete(self) -> None:
        """Soft delete the event (recoverable for 30 days)."""
        if self.is_deleted:
            raise BusinessRuleError("Event is already deleted")
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted event."""
        if not self.is_deleted:
            raise BusinessRuleError("Event is not deleted")
        self.deleted_at = None

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        event_type: str | None = None,
        event_date: date | None = None,
        event_time: time | None = None,
        end_date: date | None = None,
        location_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        color: str | None = None,
        is_recurring: bool | None = None,
        recurrence_rule: str | None = None,
        reminder_before: str | None = None,
    ) -> None:
        """Update event fields."""
        if title is not None:
            if not title.strip():
                raise BusinessRuleError("Event title cannot be empty")
            self.title = title
        if description is not None:
            self.description = description
        if event_type is not None:
            if event_type not in EVENT_TYPES:
                raise BusinessRuleError(f"Invalid event type '{event_type}'")
            self.event_type = event_type
            self.icon = EVENT_ICONS.get(event_type, "⭐")
        if event_date is not None:
            self.event_date = event_date
        if event_time is not None:
            self.event_time = event_time
        if end_date is not None:
            self.end_date = end_date
        if location_name is not None:
            self.location_name = location_name
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if color is not None:
            self.color = color
        if is_recurring is not None:
            self.is_recurring = is_recurring
        if recurrence_rule is not None:
            self.recurrence_rule = recurrence_rule
        if reminder_before is not None:
            self.reminder_before = reminder_before

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "couple_id": str(self.couple_id),
            "created_by": str(self.created_by),
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type,
            "event_date": self.event_date.isoformat(),
            "event_time": self.event_time.isoformat() if self.event_time else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "icon": self.icon,
            "is_recurring": self.is_recurring,
            "recurrence_rule": self.recurrence_rule,
            "reminder_before": self.reminder_before,
            "days_until": self.days_until,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
