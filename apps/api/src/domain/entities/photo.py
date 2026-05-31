"""Photo Domain Entity.

Represents an uploaded photo for a couple, which can optionally be linked to a calendar event.
Pure Python — no framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from domain.exceptions import BusinessRuleError


@dataclass
class Photo:
    """Photo domain entity — a couple photo/memory."""

    couple_id: UUID
    uploaded_by: UUID
    s3_key: str
    original_url: str
    id: UUID = field(default_factory=uuid4)
    event_id: UUID | None = None
    thumbnail_key: str | None = None
    thumbnail_url: str | None = None
    caption: str | None = None
    photo_date: date | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    width: int | None = None
    height: int | None = None
    file_size: int | None = None
    mime_type: str | None = None
    exif_data: dict | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate required fields."""
        if not self.s3_key.strip():
            raise BusinessRuleError("S3 key cannot be empty")
        if not self.original_url.strip():
            raise BusinessRuleError("Original URL cannot be empty")
        if not self.photo_date:
            self.photo_date = date.today()

    @property
    def is_deleted(self) -> bool:
        """Check if photo is soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Soft delete the photo."""
        if self.is_deleted:
            raise BusinessRuleError("Photo is already deleted")
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted photo."""
        if not self.is_deleted:
            raise BusinessRuleError("Photo is not deleted")
        self.deleted_at = None

    def update(
        self,
        caption: str | None = None,
        photo_date: date | None = None,
        location_name: str | None = None,
        event_id: UUID | None = None,
    ) -> None:
        """Update photo metadata."""
        if caption is not None:
            self.caption = caption
        if photo_date is not None:
            self.photo_date = photo_date
        if location_name is not None:
            self.location_name = location_name
        if event_id is not None:
            self.event_id = event_id

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "couple_id": str(self.couple_id),
            "uploaded_by": str(self.uploaded_by),
            "event_id": str(self.event_id) if self.event_id else None,
            "s3_key": self.s3_key,
            "thumbnail_key": self.thumbnail_key,
            "original_url": self.original_url,
            "thumbnail_url": self.thumbnail_url,
            "caption": self.caption,
            "photo_date": self.photo_date.isoformat() if self.photo_date else None,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "exif_data": self.exif_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
