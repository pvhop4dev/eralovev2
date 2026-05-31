---
name: celery-rules
description: Celery background task patterns, configuration, retry logic, and scheduling rules
---

# Celery Background Task Rules

## Architecture

```
FastAPI (Producer) → Redis (Broker) → Celery Worker (Consumer) → Result Backend (Redis)
```

### When to Use Celery vs Inline

| Use Celery                                | Keep Inline (async)         |
| ----------------------------------------- | --------------------------- |
| Image/video processing (resize, compress) | Simple DB queries           |
| Sending emails (welcome, reminders)       | JWT validation              |
| AI processing (sentiment analysis, Ari)   | Reading from Redis cache    |
| Push notifications (FCM batch)            | Presigned URL generation    |
| Scheduled cleanup (permanent delete)      | WebSocket message broadcast |
| Data export (ZIP generation)              | Simple CRUD operations      |
| Photobook layout generation               | Real-time status updates    |
| Weather/horoscope batch fetch             |                             |

## Configuration

```python
# apps/api/src/infrastructure/celery/config.py
from celery import Celery
from infrastructure.config import get_settings

settings = get_settings()

celery_app = Celery(
    "eralove",
    broker=settings.REDIS_URL,
    backend=f"{settings.REDIS_URL}/1",  # separate DB for results
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_acks_late=True,              # Ack after completion (at-least-once)
    worker_prefetch_multiplier=1,     # One task at a time per worker
    task_reject_on_worker_lost=True,  # Re-queue if worker crashes

    # Result backend
    result_expires=3600,              # Results expire after 1 hour
    result_backend_transport_options={
        "visibility_timeout": 3600,
    },

    # Rate limiting
    task_default_rate_limit="100/m",

    # Task routing
    task_routes={
        "tasks.notifications.*": {"queue": "notifications"},
        "tasks.media.*": {"queue": "media"},
        "tasks.ai.*": {"queue": "ai"},
        "tasks.scheduled.*": {"queue": "scheduled"},
    },

    # Periodic tasks (Celery Beat)
    beat_schedule={
        "permanent-delete-expired": {
            "task": "tasks.scheduled.permanent_delete_expired",
            "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM UTC
        },
        "fetch-daily-quotes": {
            "task": "tasks.scheduled.fetch_daily_content",
            "schedule": crontab(hour=0, minute=0),  # Daily at midnight UTC
        },
        "cleanup-expired-tokens": {
            "task": "tasks.scheduled.cleanup_expired_tokens",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM UTC
        },
        "daily-quiz-generation": {
            "task": "tasks.scheduled.generate_daily_quiz",
            "schedule": crontab(hour=22, minute=0),  # 10 PM UTC (5 AM +7)
        },
    },
)
```

## Task Patterns

### Basic Task

```python
# apps/api/src/infrastructure/celery/tasks/notifications.py
from infrastructure.celery.config import celery_app

@celery_app.task(
    name="tasks.notifications.send_push",
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 60 seconds between retries
)
def send_push_notification(self, user_id: str, title: str, body: str, data: dict | None = None):
    """Send push notification via FCM."""
    try:
        token = get_push_token(user_id)
        if not token:
            return {"status": "skipped", "reason": "no_push_token"}

        fcm_client.send(token=token, title=title, body=body, data=data)
        return {"status": "sent", "user_id": user_id}

    except FCMError as exc:
        raise self.retry(exc=exc)
```

### Task with Exponential Backoff

```python
@celery_app.task(
    name="tasks.ai.analyze_sentiment",
    bind=True,
    max_retries=3,
    autoretry_for=(ClaudeAPIError, TimeoutError),
    retry_backoff=True,          # Exponential backoff: 1s, 2s, 4s
    retry_backoff_max=300,       # Max 5 minutes between retries
    retry_jitter=True,           # Add randomness to prevent thundering herd
    soft_time_limit=30,          # Soft limit: 30 seconds
    time_limit=60,               # Hard limit: 60 seconds
)
def analyze_chat_sentiment(self, couple_id: str, message_ids: list[str]):
    """Analyze sentiment of recent messages using Claude AI."""
    messages = get_messages(message_ids)
    sentiment = claude_client.analyze(messages)

    if sentiment.tension_level > 0.7:
        # Trigger Ari warning popup via WebSocket
        send_ws_event(couple_id, "ari_sentiment_warning", {
            "tension_level": sentiment.tension_level,
            "suggestion": sentiment.suggestion,
        })

    save_sentiment_result(couple_id, sentiment)
    return {"tension_level": sentiment.tension_level}
```

### Chained Tasks (Pipeline)

```python
from celery import chain

# Process photo upload: resize → compress → generate thumbnail → notify
photo_pipeline = chain(
    resize_photo.s(photo_id, max_width=2000),
    compress_photo.s(quality=85),
    generate_thumbnail.s(width=300, height=300),
    notify_partner.s(uploader_id=user_id),
)
photo_pipeline.apply_async()
```

### Group Tasks (Parallel)

```python
from celery import group

# Send anniversary reminders to all couples
reminder_group = group(
    send_anniversary_reminder.s(couple_id)
    for couple_id in couple_ids_with_upcoming_anniversary
)
result = reminder_group.apply_async()
```

## Calling Tasks from FastAPI

### In Use Cases (Application Layer)

```python
# apps/api/src/application/use_cases/chat/send_message.py
class SendMessageUseCase:
    def __init__(self, message_repo, couple_repo, task_dispatcher):
        self.message_repo = message_repo
        self.couple_repo = couple_repo
        self.task_dispatcher = task_dispatcher  # Interface, not Celery directly

    async def execute(self, dto: SendMessageRequest, user_id: UUID) -> MessageResponse:
        # ... save message to DB
        message = await self.message_repo.create(...)

        # Dispatch background tasks (non-blocking)
        self.task_dispatcher.send_push_notification(
            user_id=str(partner.id),
            title=f"💬 {user.display_name}",
            body=dto.content[:100],
        )

        # Sentiment analysis every 10 messages
        if await self.message_repo.count_since_last_analysis(couple.id) >= 10:
            self.task_dispatcher.analyze_sentiment(
                couple_id=str(couple.id),
                message_ids=[str(m.id) for m in recent_messages],
            )

        return MessageResponse.model_validate(message)
```

### Task Dispatcher Interface (Clean Architecture)

```python
# apps/api/src/application/interfaces/task_dispatcher.py
from abc import ABC, abstractmethod

class TaskDispatcher(ABC):
    @abstractmethod
    def send_push_notification(self, user_id: str, title: str, body: str) -> None: ...

    @abstractmethod
    def send_email(self, to: str, template: str, context: dict) -> None: ...

    @abstractmethod
    def analyze_sentiment(self, couple_id: str, message_ids: list[str]) -> None: ...

    @abstractmethod
    def process_photo(self, photo_id: str) -> None: ...

# apps/api/src/infrastructure/celery/task_dispatcher.py
class CeleryTaskDispatcher(TaskDispatcher):
    def send_push_notification(self, user_id: str, title: str, body: str) -> None:
        send_push_notification.delay(user_id, title, body)

    def analyze_sentiment(self, couple_id: str, message_ids: list[str]) -> None:
        analyze_chat_sentiment.delay(couple_id, message_ids)
```

## Scheduled Tasks (Celery Beat)

### Permanent Deletion (30-day policy)

```python
@celery_app.task(name="tasks.scheduled.permanent_delete_expired")
def permanent_delete_expired():
    """Permanently delete records soft-deleted more than 30 days ago."""
    cutoff = datetime.now(UTC) - timedelta(days=30)

    # Delete from S3 first, then DB
    expired_photos = get_expired_photos(cutoff)
    for photo in expired_photos:
        s3_client.delete_object(photo.s3_key)

    # Permanent delete from DB
    count = permanently_delete_before(cutoff)
    logger.info("permanent_delete_completed", count=count, cutoff=str(cutoff))
```

## Worker Commands

```bash
# Start worker (development)
cd apps/api && celery -A infrastructure.celery.config worker --loglevel=info

# Start worker with specific queues
celery -A infrastructure.celery.config worker -Q notifications,media --loglevel=info

# Start Celery Beat (scheduler)
celery -A infrastructure.celery.config beat --loglevel=info

# Start both worker + beat (dev only)
celery -A infrastructure.celery.config worker --beat --loglevel=info

# Monitor tasks (Flower)
celery -A infrastructure.celery.config flower --port=5555

# Inspect active tasks
celery -A infrastructure.celery.config inspect active
```

## Docker Setup

```yaml
# docker-compose.yml
celery-worker:
  build: ./apps/api
  command: celery -A infrastructure.celery.config worker -Q default,notifications,media,ai --loglevel=info
  depends_on:
    - redis
    - postgres
  environment:
    - REDIS_URL=redis://redis:6379/0
    - DATABASE_URL=postgresql+asyncpg://...

celery-beat:
  build: ./apps/api
  command: celery -A infrastructure.celery.config beat --loglevel=info
  depends_on:
    - redis
```

## Rules

### MUST

- All tasks MUST be idempotent (safe to retry)
- All task arguments MUST be JSON-serializable (str, int, list, dict — NO UUID, datetime objects)
- Use `bind=True` for tasks that need retry logic
- Set `max_retries` on all tasks (default: 3)
- Set `soft_time_limit` and `time_limit` on all tasks
- Use task dispatcher interface in application layer (not import Celery directly)

### MUST NOT

- Never pass ORM model objects as task arguments (use IDs, strings)
- Never use `task.get()` synchronously inside FastAPI async routes (it blocks!)
- Never run database sessions inside Celery tasks without proper cleanup
- Never store large payloads in task arguments (use S3/DB reference instead)

### SHOULD

- Use separate queues for different task types (notifications, media, ai)
- Use exponential backoff with jitter for external API calls
- Log task start, completion, and failure with structured logging
- Monitor task queues and failure rates (Flower or Prometheus)
