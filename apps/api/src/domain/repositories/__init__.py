"""Repositories package."""

from domain.repositories.couple_repository import CoupleRepository
from domain.repositories.event_repository import LoveEventRepository
from domain.repositories.match_repository import MatchRequestRepository
from domain.repositories.message_repository import MessageRepository
from domain.repositories.oauth_account_repository import OAuthAccountRepository
from domain.repositories.photo_repository import PhotoRepository
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from domain.repositories.user_repository import UserRepository

__all__ = [
    "CoupleRepository",
    "LoveEventRepository",
    "MatchRequestRepository",
    "MessageRepository",
    "OAuthAccountRepository",
    "PhotoRepository",
    "RefreshTokenRepository",
    "UserRepository",
]
