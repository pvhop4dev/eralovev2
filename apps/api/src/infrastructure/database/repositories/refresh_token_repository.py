"""PostgreSQL Refresh Token Repository Implementation."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.refresh_token import RefreshToken
from domain.repositories.refresh_token_repository import RefreshTokenRepository
from infrastructure.database.models.refresh_token_model import RefreshTokenModel


class PostgresRefreshTokenRepository(RefreshTokenRepository):
    """PostgreSQL-backed refresh token repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        """Persist a new refresh token."""
        model = RefreshTokenModel(
            id=token.id,
            user_id=token.user_id,
            token_hash=token.token_hash,
            device_info=token.device_info,
            expires_at=token.expires_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve a refresh token by its SHA256 hash."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete_by_hash(self, token_hash: str) -> None:
        """Delete/revoke a specific refresh token by its hash."""
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_all_for_user(self, user_id: UUID) -> None:
        """Delete/revoke all refresh tokens belonging to a user (force logout)."""
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()

    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        """Convert database model to domain entity."""
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            device_info=model.device_info,
        )
