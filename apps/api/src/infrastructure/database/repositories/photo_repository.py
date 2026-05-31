"""PostgreSQL Photo Repository Implementation."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.photo import Photo
from domain.repositories.photo_repository import PhotoRepository
from infrastructure.database.models.photo_model import PhotoModel


class PostgresPhotoRepository(PhotoRepository):
    """PostgreSQL-backed photo repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, photo: Photo) -> Photo:
        model = PhotoModel(
            id=photo.id,
            couple_id=photo.couple_id,
            uploaded_by=photo.uploaded_by,
            event_id=photo.event_id,
            s3_key=photo.s3_key,
            thumbnail_key=photo.thumbnail_key,
            original_url=photo.original_url,
            thumbnail_url=photo.thumbnail_url,
            caption=photo.caption,
            photo_date=photo.photo_date,
            location_name=photo.location_name,
            latitude=photo.latitude,
            longitude=photo.longitude,
            width=photo.width,
            height=photo.height,
            file_size=photo.file_size,
            mime_type=photo.mime_type,
            exif_data=photo.exif_data,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, photo_id: UUID) -> Photo | None:
        stmt = select(PhotoModel).where(
            PhotoModel.id == photo_id,
            PhotoModel.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_couple(
        self, couple_id: UUID, limit: int = 50, before_id: UUID | None = None
    ) -> list[Photo]:
        stmt = (
            select(PhotoModel)
            .where(
                PhotoModel.couple_id == couple_id,
                PhotoModel.deleted_at.is_(None),
            )
            .order_by(PhotoModel.created_at.desc())
            .limit(limit)
        )
        if before_id:
            # Cursor-based pagination
            subq = select(PhotoModel.created_at).where(PhotoModel.id == before_id).scalar_subquery()
            stmt = stmt.where(PhotoModel.created_at < subq)

        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_event(self, event_id: UUID) -> list[Photo]:
        stmt = (
            select(PhotoModel)
            .where(
                PhotoModel.event_id == event_id,
                PhotoModel.deleted_at.is_(None),
            )
            .order_by(PhotoModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, photo: Photo) -> Photo:
        stmt = select(PhotoModel).where(PhotoModel.id == photo.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            from domain.exceptions import NotFoundError

            raise NotFoundError("Photo not found")

        model.event_id = photo.event_id
        model.caption = photo.caption
        model.photo_date = photo.photo_date
        model.location_name = photo.location_name
        model.deleted_at = photo.deleted_at

        await self.session.flush()
        return self._to_entity(model)

    async def soft_delete(self, photo_id: UUID) -> None:
        stmt = select(PhotoModel).where(PhotoModel.id == photo_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.deleted_at = datetime.now(UTC)
            await self.session.flush()

    @staticmethod
    def _to_entity(model: PhotoModel) -> Photo:
        return Photo(
            id=model.id,
            couple_id=model.couple_id,
            uploaded_by=model.uploaded_by,
            event_id=model.event_id,
            s3_key=model.s3_key,
            thumbnail_key=model.thumbnail_key,
            original_url=model.original_url,
            thumbnail_url=model.thumbnail_url,
            caption=model.caption,
            photo_date=model.photo_date,
            location_name=model.location_name,
            latitude=float(model.latitude) if model.latitude else None,
            longitude=float(model.longitude) if model.longitude else None,
            width=model.width,
            height=model.height,
            file_size=model.file_size,
            mime_type=model.mime_type,
            exif_data=model.exif_data,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )
