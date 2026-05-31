"""Photo DTOs (Data Transfer Objects)."""

from datetime import date

from pydantic import BaseModel, Field


class AddPhotoRequest(BaseModel):
    """Request DTO for adding a new photo."""

    s3_key: str = Field(..., min_length=1, max_length=500)
    original_url: str = Field(..., min_length=1)
    thumbnail_key: str | None = Field(None, max_length=500)
    thumbnail_url: str | None = None
    caption: str | None = None
    photo_date: date | None = None
    location_name: str | None = Field(None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    width: int | None = None
    height: int | None = None
    file_size: int | None = None
    mime_type: str | None = Field(None, max_length=50)
    exif_data: dict | None = None
    event_id: str | None = None


class PhotoResponse(BaseModel):
    """Response DTO for photo details."""

    id: str
    couple_id: str
    uploaded_by: str
    event_id: str | None = None
    s3_key: str
    thumbnail_key: str | None = None
    original_url: str
    thumbnail_url: str | None = None
    caption: str | None = None
    photo_date: str | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    width: int | None = None
    height: int | None = None
    file_size: int | None = None
    mime_type: str | None = None
    exif_data: dict | None = None
    created_at: str | None = None
