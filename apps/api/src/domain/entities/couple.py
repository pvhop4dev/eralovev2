"""Couple Domain Entity.

Represents the relationship between two matched users.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleError


@dataclass
class Couple:
    """Couple entity — two users in an active relationship."""

    user1_id: UUID
    user2_id: UUID
    start_date: date
    id: UUID = field(default_factory=uuid4)
    couple_photo_url: str | None = None
    status: str = "active"  # active, paused, broken_up
    theme_color: str = "rose"
    wallpaper_url: str | None = None
    nicknames: dict | None = None
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    paused_at: datetime | None = None
    broken_up_at: datetime | None = None

    @property
    def days_together(self) -> int:
        """Calculate total days together from start_date."""
        return (date.today() - self.start_date).days

    @property
    def is_active(self) -> bool:
        """Check if couple is currently active."""
        return self.status == "active"

    @property
    def is_paused(self) -> bool:
        """Check if couple is currently paused."""
        return self.status == "paused"

    def has_user(self, user_id: UUID) -> bool:
        """Check if a user is part of this couple."""
        return user_id in (self.user1_id, self.user2_id)

    def get_partner_id(self, user_id: UUID) -> UUID:
        """Get the partner's user_id.

        Args:
            user_id: The current user's ID.

        Returns:
            The partner's UUID.

        Raises:
            BusinessRuleError: If user is not part of this couple.
        """
        if user_id == self.user1_id:
            return self.user2_id
        elif user_id == self.user2_id:
            return self.user1_id
        raise BusinessRuleError("User is not part of this couple")

    def pause(self) -> None:
        """Pause the relationship.

        Raises:
            BusinessRuleError: If already paused or broken up.
        """
        if self.status != "active":
            raise BusinessRuleError(f"Cannot pause — current status is '{self.status}'")
        self.status = "paused"
        self.paused_at = datetime.now(UTC)

    def resume(self) -> None:
        """Resume the relationship after a pause.

        Raises:
            BusinessRuleError: If not currently paused.
        """
        if self.status != "paused":
            raise BusinessRuleError("Cannot resume — relationship is not paused")
        self.status = "active"
        self.paused_at = None

    def break_up(self) -> None:
        """Break up the couple (soft — data is preserved).

        Raises:
            BusinessRuleError: If already broken up.
        """
        if self.status == "broken_up":
            raise BusinessRuleError("Already broken up")
        self.status = "broken_up"
        self.broken_up_at = datetime.now(UTC)

    def update_settings(
        self,
        couple_photo_url: str | None = None,
        theme_color: str | None = None,
        wallpaper_url: str | None = None,
        nicknames: dict | None = None,
    ) -> None:
        """Update couple settings."""
        if couple_photo_url is not None:
            self.couple_photo_url = couple_photo_url
        if theme_color is not None:
            self.theme_color = theme_color
        if wallpaper_url is not None:
            self.wallpaper_url = wallpaper_url
        if nicknames is not None:
            self.nicknames = nicknames

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "user1_id": str(self.user1_id),
            "user2_id": str(self.user2_id),
            "start_date": self.start_date.isoformat(),
            "couple_photo_url": self.couple_photo_url,
            "status": self.status,
            "theme_color": self.theme_color,
            "wallpaper_url": self.wallpaper_url,
            "nicknames": self.nicknames,
            "days_together": self.days_together,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
