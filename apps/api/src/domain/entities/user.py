"""User Entity.

Core domain entity representing a user of Eralove.
Pure Python — no framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

# Zodiac sign mapping by month-day ranges
_ZODIAC_RANGES: list[tuple[tuple[int, int], tuple[int, int], str]] = [
    ((1, 20), (2, 18), "Aquarius"),
    ((2, 19), (3, 20), "Pisces"),
    ((3, 21), (4, 19), "Aries"),
    ((4, 20), (5, 20), "Taurus"),
    ((5, 21), (6, 20), "Gemini"),
    ((6, 21), (7, 22), "Cancer"),
    ((7, 23), (8, 22), "Leo"),
    ((8, 23), (9, 22), "Virgo"),
    ((9, 23), (10, 22), "Libra"),
    ((10, 23), (11, 21), "Scorpio"),
    ((11, 22), (12, 21), "Sagittarius"),
    ((12, 22), (1, 19), "Capricorn"),
]


def _calculate_zodiac(dob: date) -> str:
    """Calculate zodiac sign from date of birth."""
    month, day = dob.month, dob.day
    for (start_m, start_d), (end_m, end_d), sign in _ZODIAC_RANGES:
        if sign == "Capricorn":
            if (month == 12 and day >= 22) or (month == 1 and day <= 19):
                return sign
        elif (month == start_m and day >= start_d) or (
            month == end_m and day <= end_d
        ):
            return sign
    return "Unknown"


@dataclass
class User:
    """User domain entity.

    Represents a registered user of Eralove with their profile,
    preferences, and account status.
    """

    id: UUID = field(default_factory=uuid4)
    email: str = ""
    password_hash: str | None = None
    display_name: str = ""
    username: str = ""
    avatar_url: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    zodiac_sign: str | None = None
    love_language: str | None = None
    bio: str | None = None
    is_email_verified: bool = False
    is_onboarded: bool = False
    two_factor_enabled: bool = False
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Auto-calculate zodiac sign from DOB if not set."""
        if self.date_of_birth and not self.zodiac_sign:
            self.zodiac_sign = _calculate_zodiac(self.date_of_birth)

    @property
    def is_deleted(self) -> bool:
        """Check if user account is soft-deleted."""
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        """Check if user account is active (verified and not deleted)."""
        return self.is_email_verified and not self.is_deleted

    @property
    def age(self) -> int | None:
        """Calculate user's age from date of birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        ):
            age -= 1
        return age

    def verify_email(self) -> None:
        """Mark email as verified."""
        self.is_email_verified = True

    def complete_onboarding(
        self,
        display_name: str,
        date_of_birth: date | None = None,
        love_language: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """Complete the onboarding process with profile data."""
        self.display_name = display_name
        if date_of_birth:
            self.date_of_birth = date_of_birth
            self.zodiac_sign = _calculate_zodiac(date_of_birth)
        if love_language:
            self.love_language = love_language
        if avatar_url:
            self.avatar_url = avatar_url
        self.is_onboarded = True

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        from datetime import timezone

        self.last_login_at = datetime.now(timezone.utc)

    def soft_delete(self) -> None:
        """Soft delete the user account."""
        from datetime import timezone

        if self.is_deleted:
            from domain.exceptions import AlreadyDeletedError

            raise AlreadyDeletedError("User account is already deleted")
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted user account."""
        if not self.is_deleted:
            from domain.exceptions import NotDeletedError

            raise NotDeletedError("User account is not deleted")
        self.deleted_at = None

    def to_dict(self) -> dict:
        """Convert entity to dictionary for persistence."""
        return {
            "id": self.id,
            "email": self.email,
            "password_hash": self.password_hash,
            "display_name": self.display_name,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "zodiac_sign": self.zodiac_sign,
            "love_language": self.love_language,
            "bio": self.bio,
            "is_email_verified": self.is_email_verified,
            "is_onboarded": self.is_onboarded,
            "two_factor_enabled": self.two_factor_enabled,
            "last_login_at": self.last_login_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
        }
