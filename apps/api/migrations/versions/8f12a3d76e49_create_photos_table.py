"""create_photos_table

Revision ID: 8f12a3d76e49
Revises: 2a09c4185830
Create Date: 2026-05-31 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f12a3d76e49'
down_revision: Union[str, None] = '2a09c4185830'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create photos table
    op.create_table(
        'photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('couple_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('s3_key', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_key', sa.String(length=500), nullable=True),
        sa.Column('original_url', sa.Text(), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('photo_date', sa.Date(), nullable=True),
        sa.Column('location_name', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(length=50), nullable=True),
        sa.Column('exif_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['love_events.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_photos_couple_id'), 'photos', ['couple_id'], unique=False)
    op.create_index(op.f('ix_photos_event_id'), 'photos', ['event_id'], unique=False)
    op.create_index(op.f('ix_photos_photo_date'), 'photos', ['photo_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_photos_photo_date'), table_name='photos')
    op.drop_index(op.f('ix_photos_event_id'), table_name='photos')
    op.drop_index(op.f('ix_photos_couple_id'), table_name='photos')
    op.drop_table('photos')
