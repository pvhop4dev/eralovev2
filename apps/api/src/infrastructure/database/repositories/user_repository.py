"""PostgreSQL User Repository Implementation.

Concrete implementation of UserRepository using SQLAlchemy async.
"""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models.user_model import UserModel


class PostgresUserRepository(UserRepository):
    """PostgreSQL-backed user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Persist a new user."""
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            display_name=user.display_name,
            username=user.username,
            avatar_url=user.avatar_url,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            zodiac_sign=user.zodiac_sign,
            love_language=user.love_language,
            bio=user.bio,
            is_email_verified=user.is_email_verified,
            is_onboarded=user.is_onboarded,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID (excludes soft-deleted)."""
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email (case-insensitive, excludes soft-deleted)."""
        stmt = select(UserModel).where(
            UserModel.email == email.lower(),
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username (excludes soft-deleted)."""
        stmt = select(UserModel).where(
            UserModel.username == username,
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import UserNotFoundError
            raise UserNotFoundError()

        # Update fields
        model.email = user.email
        model.password_hash = user.password_hash
        model.display_name = user.display_name
        model.username = user.username
        model.avatar_url = user.avatar_url
        model.date_of_birth = user.date_of_birth
        model.gender = user.gender
        model.zodiac_sign = user.zodiac_sign
        model.love_language = user.love_language
        model.bio = user.bio
        model.is_email_verified = user.is_email_verified
        model.is_onboarded = user.is_onboarded
        model.two_factor_enabled = user.two_factor_enabled
        model.last_login_at = user.last_login_at
        model.deleted_at = user.deleted_at

        await self.session.flush()
        return self._to_entity(model)

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        stmt = select(UserModel.id).where(
            UserModel.email == email.lower(),
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username is already taken."""
        stmt = select(UserModel.id).where(
            UserModel.username == username,
            UserModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def search(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> list[User]:
        """Search users by username or display_name."""
        search_pattern = f"%{query}%"
        stmt = (
            select(UserModel)
            .where(
                UserModel.deleted_at.is_(None),
                or_(
                    UserModel.username.ilike(search_pattern),
                    UserModel.display_name.ilike(search_pattern),
                ),
            )
            .order_by(UserModel.display_name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            display_name=model.display_name,
            username=model.username,
            avatar_url=model.avatar_url,
            date_of_birth=model.date_of_birth,
            gender=model.gender,
            zodiac_sign=model.zodiac_sign,
            love_language=model.love_language,
            bio=model.bio,
            is_email_verified=model.is_email_verified,
            is_onboarded=model.is_onboarded,
            two_factor_enabled=model.two_factor_enabled,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
