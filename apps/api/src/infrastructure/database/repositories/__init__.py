"""Database repositories package."""

from infrastructure.database.repositories.couple_repository import PostgresCoupleRepository
from infrastructure.database.repositories.event_repository import PostgresLoveEventRepository
from infrastructure.database.repositories.match_repository import PostgresMatchRequestRepository
from infrastructure.database.repositories.message_repository import PostgresMessageRepository
from infrastructure.database.repositories.oauth_account_repository import (
    PostgresOAuthAccountRepository,
)
from infrastructure.database.repositories.photo_repository import PostgresPhotoRepository
from infrastructure.database.repositories.refresh_token_repository import (
    PostgresRefreshTokenRepository,
)
from infrastructure.database.repositories.user_repository import PostgresUserRepository

__all__ = [
    "PostgresCoupleRepository",
    "PostgresLoveEventRepository",
    "PostgresMatchRequestRepository",
    "PostgresMessageRepository",
    "PostgresOAuthAccountRepository",
    "PostgresPhotoRepository",
    "PostgresRefreshTokenRepository",
    "PostgresUserRepository",
]
