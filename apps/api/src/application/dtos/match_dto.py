"""Match & Couple DTOs."""

from datetime import date

from pydantic import BaseModel, Field


class SendMatchRequestDTO(BaseModel):
    receiver_id: str = Field(..., description="UUID of the user to match with")
    message: str | None = Field(None, max_length=500, description="Optional message")
    proposed_start_date: date | None = Field(None, description="Proposed relationship start date")


class AcceptMatchRequestDTO(BaseModel):
    start_date: date = Field(default_factory=date.today, description="Couple start date")


class DeclineMatchRequestDTO(BaseModel):
    reason: str | None = Field(None, max_length=500)


class MatchRequestResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    message: str | None = None
    status: str
    proposed_start_date: date | None = None
    expires_at: str | None = None
    created_at: str | None = None
    sender_name: str | None = None
    sender_username: str | None = None
    sender_avatar: str | None = None
    receiver_name: str | None = None
    receiver_username: str | None = None


class CoupleResponse(BaseModel):
    id: str
    user1_id: str
    user2_id: str
    start_date: date
    couple_photo_url: str | None = None
    status: str
    theme_color: str = "rose"
    wallpaper_url: str | None = None
    nicknames: dict | None = None
    days_together: int = 0


class UpdateCoupleDTO(BaseModel):
    couple_photo_url: str | None = None
    theme_color: str | None = None
    wallpaper_url: str | None = None
    nicknames: dict | None = None


class OnboardingRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date | None = None
    love_language: str | None = Field(None, max_length=50)
    avatar_url: str | None = None


class UnmatchRequest(BaseModel):
    confirmation_code: str | None = Field(
        None, max_length=100, description="Optional confirmation string"
    )
