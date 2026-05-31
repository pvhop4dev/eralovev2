"""initial_migration

Revision ID: 2a09c4185830
Revises: 
Create Date: 2026-05-31 09:11:02.319764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2a09c4185830'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('zodiac_sign', sa.String(length=20), nullable=True),
        sa.Column('love_language', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False),
        sa.Column('is_onboarded', sa.Boolean(), nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False),
        sa.Column('two_factor_secret', sa.String(length=255), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)

    # 2. couples table
    op.create_table(
        'couples',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user1_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user2_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('couple_photo_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('theme_color', sa.String(length=20), nullable=False),
        sa.Column('wallpaper_url', sa.Text(), nullable=True),
        sa.Column('nicknames', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('broken_up_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_couples_user1_id'), 'couples', ['user1_id'], unique=False)
    op.create_index(op.f('ix_couples_user2_id'), 'couples', ['user2_id'], unique=False)
    op.create_index(op.f('ix_couples_status'), 'couples', ['status'], unique=False)

    # 3. love_events table
    op.create_table(
        'love_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('couple_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=30), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_time', sa.Time(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('location_name', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('recurrence_rule', sa.String(length=100), nullable=True),
        sa.Column('reminder_before', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_love_events_couple_id'), 'love_events', ['couple_id'], unique=False)
    op.create_index(op.f('ix_love_events_event_type'), 'love_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_love_events_event_date'), 'love_events', ['event_date'], unique=False)

    # 4. messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('couple_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('media_url', sa.Text(), nullable=True),
        sa.Column('media_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reply_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reply_to_id'], ['messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_couple_id'), 'messages', ['couple_id'], unique=False)

    # 5. match_requests table
    op.create_table(
        'match_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('proposed_start_date', sa.Date(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_requests_sender_id'), 'match_requests', ['sender_id'], unique=False)
    op.create_index(op.f('ix_match_requests_receiver_id'), 'match_requests', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_match_requests_status'), 'match_requests', ['status'], unique=False)

    # 6. oauth_accounts table
    op.create_table(
        'oauth_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('provider_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_id', name='uq_oauth_provider_id')
    )
    op.create_index(op.f('ix_oauth_accounts_user_id'), 'oauth_accounts', ['user_id'], unique=False)

    # 7. refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('device_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    
    op.drop_index(op.f('ix_oauth_accounts_user_id'), table_name='oauth_accounts')
    op.drop_table('oauth_accounts')
    
    op.drop_index(op.f('ix_match_requests_status'), table_name='match_requests')
    op.drop_index(op.f('ix_match_requests_receiver_id'), table_name='match_requests')
    op.drop_index(op.f('ix_match_requests_sender_id'), table_name='match_requests')
    op.drop_table('match_requests')
    
    op.drop_index(op.f('ix_messages_couple_id'), table_name='messages')
    op.drop_table('messages')
    
    op.drop_index(op.f('ix_love_events_event_date'), table_name='love_events')
    op.drop_index(op.f('ix_love_events_event_type'), table_name='love_events')
    op.drop_index(op.f('ix_love_events_couple_id'), table_name='love_events')
    op.drop_table('love_events')
    
    op.drop_index(op.f('ix_couples_status'), table_name='couples')
    op.drop_index(op.f('ix_couples_user2_id'), table_name='couples')
    op.drop_index(op.f('ix_couples_user1_id'), table_name='couples')
    op.drop_table('couples')
    
    op.drop_index(op.f('ix_users_deleted_at'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    sa.orm.session.Session.close_all() # close any sessions if active
    op.drop_table('users')

