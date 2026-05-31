---
name: soft-delete
description: Soft delete pattern rules — when to use, how to implement, and how to query
---

# Soft Delete Rules

## When to Use Soft Delete

### MUST soft delete (user-facing data that may need recovery):
- `love_events` — events can be restored within 30 days
- `photos` — photos can be recovered
- `messages` — deleted messages hidden but retained for compliance
- `shared_notes` — notes can be recovered
- `users` — account deactivation before permanent deletion
- `couples` — relationship data preserved on unmatch (hidden, not destroyed)

### MUST hard delete (no recovery needed):
- `refresh_tokens` — expired tokens, no value in keeping
- `push_tokens` — device tokens, replace on re-register
- `message_reactions` — reactions can just be re-added
- `shared_todo_items` — checked-off items, low value
- `coin_transactions` — never delete (audit trail), but never soft delete either
- `login_history` — auto-purge after 90 days, no soft delete
- `mood_checkins` — immutable records, never delete

### NEVER delete (immutable audit trail):
- `coin_transactions`
- `login_history`
- `call_logs`
- `quiz_answers`

---

## Implementation

### SQLAlchemy Model Mixin
```python
# apps/api/src/infrastructure/database/mixins.py
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### Model Usage
```python
class EventModel(Base, SoftDeleteMixin):
    __tablename__ = "love_events"
    # ... columns
    # deleted_at inherited from SoftDeleteMixin
```

### Domain Entity
```python
# apps/api/src/domain/entities/event.py
@dataclass
class Event:
    id: UUID
    title: str
    deleted_at: datetime | None = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        if self.is_deleted:
            raise AlreadyDeletedError(f"Event {self.id} is already deleted")
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        if not self.is_deleted:
            raise NotDeletedError(f"Event {self.id} is not deleted")
        self.deleted_at = None
```

---

## Repository Query Rules

### CRITICAL: Always Filter Out Deleted Records
Every SELECT query on a soft-deletable table MUST include `WHERE deleted_at IS NULL` unless explicitly querying deleted records.

```python
# CORRECT — default queries exclude deleted
class PostgresEventRepository(EventRepository):
    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = (
            select(EventModel)
            .where(EventModel.id == event_id)
            .where(EventModel.deleted_at.is_(None))   # <-- REQUIRED
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_couple(self, couple_id: UUID) -> list[Event]:
        stmt = (
            select(EventModel)
            .where(EventModel.couple_id == couple_id)
            .where(EventModel.deleted_at.is_(None))   # <-- REQUIRED
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

```python
# CORRECT — explicit method for including deleted
    async def get_by_id_including_deleted(self, event_id: UUID) -> Event | None:
        """For restore operations only."""
        stmt = select(EventModel).where(EventModel.id == event_id)
        # NO deleted_at filter
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_deleted_by_couple(self, couple_id: UUID) -> list[Event]:
        """For trash/recycle bin view."""
        stmt = (
            select(EventModel)
            .where(EventModel.couple_id == couple_id)
            .where(EventModel.deleted_at.is_not(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

### WRONG — Missing filter
```python
# WRONG! This returns deleted records too
async def get_by_id(self, event_id: UUID) -> Event | None:
    stmt = select(EventModel).where(EventModel.id == event_id)
    # Missing: .where(EventModel.deleted_at.is_(None))
```

---

## Soft Delete Use Case Pattern
```python
# apps/api/src/application/use_cases/calendar/delete_event.py
class DeleteEventUseCase:
    def __init__(self, event_repo: EventRepository, couple_repo: CoupleRepository):
        self.event_repo = event_repo
        self.couple_repo = couple_repo

    async def execute(self, event_id: UUID, user_id: UUID) -> None:
        # 1. Verify user belongs to couple
        couple = await self.couple_repo.get_by_user(user_id)
        if not couple:
            raise CoupleNotFoundError()

        # 2. Get event (active only)
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise EventNotFoundError()

        # 3. Verify event belongs to this couple
        if event.couple_id != couple.id:
            raise ForbiddenError()

        # 4. Soft delete via domain method
        event.soft_delete()
        await self.event_repo.update(event)
```

## Restore Use Case Pattern
```python
class RestoreEventUseCase:
    RESTORE_WINDOW_DAYS = 30

    async def execute(self, event_id: UUID, user_id: UUID) -> Event:
        couple = await self.couple_repo.get_by_user(user_id)
        if not couple:
            raise CoupleNotFoundError()

        # Use special method that includes deleted records
        event = await self.event_repo.get_by_id_including_deleted(event_id)
        if not event:
            raise EventNotFoundError()

        if event.couple_id != couple.id:
            raise ForbiddenError()

        if not event.is_deleted:
            raise NotDeletedError()

        # Check restore window
        days_since_deletion = (datetime.now(UTC) - event.deleted_at).days
        if days_since_deletion > self.RESTORE_WINDOW_DAYS:
            raise RestoreWindowExpiredError(
                f"Event was deleted {days_since_deletion} days ago. "
                f"Restore window is {self.RESTORE_WINDOW_DAYS} days."
            )

        event.restore()
        await self.event_repo.update(event)
        return event
```

---

## API Response Rules
- `DELETE /events/{id}` → returns `204 No Content` (soft delete)
- `POST /events/{id}/restore` → returns `200` with restored event
- `GET /events` → NEVER returns soft-deleted records
- `GET /events/trash` → returns only soft-deleted records (for recovery UI)
- Soft-deleted records excluded from search, calendar view, map pins, statistics

## Permanent Deletion
- Background job runs daily: permanently delete records where `deleted_at < now() - 30 days`
- S3 objects (photos/files) deleted only during permanent deletion, not soft delete
- Use case: `PermanentDeleteExpiredUseCase` (Celery task)

## Cascade Rules
- When a `couple` is soft-deleted (unmatch): all related events, photos, messages get soft-deleted too
- When an `event` is soft-deleted: associated photos remain (they can exist standalone)
- When a `user` requests account deletion: soft-delete first, schedule permanent deletion after 30 days

## Database Index
Always index `deleted_at` for efficient filtering:
```sql
CREATE INDEX idx_events_deleted ON love_events(deleted_at) WHERE deleted_at IS NULL;
```
This partial index speeds up the most common query (active records only).

## Testing Soft Delete
```python
@pytest.mark.asyncio
async def test_delete_event_sets_deleted_at():
    event = EventFactory.create()
    assert event.deleted_at is None

    event.soft_delete()

    assert event.deleted_at is not None
    assert event.is_deleted is True

@pytest.mark.asyncio
async def test_get_by_id_excludes_deleted_events():
    # Integration test
    deleted_event = await create_event(deleted_at=datetime.now(UTC))
    result = await event_repo.get_by_id(deleted_event.id)
    assert result is None

@pytest.mark.asyncio
async def test_restore_expired_event_raises_error():
    event = EventFactory.create(
        deleted_at=datetime.now(UTC) - timedelta(days=31)
    )
    use_case = RestoreEventUseCase(...)

    with pytest.raises(RestoreWindowExpiredError):
        await use_case.execute(event.id, user_id)
```
