"""PostgreSQL OAuth Account Repository Implementation."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.oauth_account import OAuthAccount
from domain.repositories.oauth_account_repository import OAuthAccountRepository
from infrastructure.database.models.oauth_account_model import OAuthAccountModel


class PostgresOAuthAccountRepository(OAuthAccountRepository):
    """PostgreSQL-backed OAuth account repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, oauth_account: OAuthAccount) -> OAuthAccount:
        """Persist a new OAuth account connection."""
        model = OAuthAccountModel(
            id=oauth_account.id,
            user_id=oauth_account.user_id,
            provider=oauth_account.provider,
            provider_id=oauth_account.provider_id,
            email=oauth_account.email,
            metadata_=oauth_account.metadata,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_provider(self, provider: str, provider_id: str) -> OAuthAccount | None:
        """Retrieve an OAuth account by provider name and provider's user ID."""
        stmt = select(OAuthAccountModel).where(
            OAuthAccountModel.provider == provider,
            OAuthAccountModel.provider_id == provider_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> list[OAuthAccount]:
        """Retrieve all OAuth connections for a user."""
        stmt = select(OAuthAccountModel).where(OAuthAccountModel.user_id == user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def delete(self, id: UUID) -> None:
        """Delete/unlink an OAuth account connection."""
        stmt = delete(OAuthAccountModel).where(OAuthAccountModel.id == id)
        await self.session.execute(stmt)
        await self.session.flush()

    @staticmethod
    def _to_entity(model: OAuthAccountModel) -> OAuthAccount:
        """Convert database model to domain entity."""
        return OAuthAccount(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            provider_id=model.provider_id,
            email=model.email,
            metadata=model.metadata_,
            created_at=model.created_at,
        )
