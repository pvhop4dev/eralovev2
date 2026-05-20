---
name: create-celery-task
description: Create a new Celery background task with retry logic, scheduling, and proper integration
---

# Create Celery Background Task

When asked to create a background task, follow this pattern:

## 1. Define the Task

```python
# apps/api/src/infrastructure/celery/tasks/{domain}.py
from infrastructure.celery.config import celery_app
import structlog

logger = structlog.get_logger()

@celery_app.task(
    name="tasks.{domain}.{action}",
    bind=True,
    max_retries=3,
    autoretry_for=(ExternalServiceError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    soft_time_limit=30,
    time_limit=60,
)
def {action}_{resource}(self, resource_id: str, **kwargs):
    """Description of what this task does."""
    logger.info("task_started", task=self.name, resource_id=resource_id)
    try:
        # Business logic here
        result = do_work(resource_id, **kwargs)
        logger.info("task_completed", task=self.name, resource_id=resource_id)
        return {"status": "success", "result": result}
    except RetryableError as exc:
        logger.warning("task_retrying", task=self.name, error=str(exc))
        raise self.retry(exc=exc)
    except Exception as exc:
        logger.error("task_failed", task=self.name, error=str(exc))
        raise
```

## 2. Add Task Dispatcher Interface Method

```python
# apps/api/src/application/interfaces/task_dispatcher.py
class TaskDispatcher(ABC):
    # ... existing methods
    @abstractmethod
    def {action}_{resource}(self, resource_id: str, **kwargs) -> None: ...
```

## 3. Implement in CeleryTaskDispatcher

```python
# apps/api/src/infrastructure/celery/task_dispatcher.py
class CeleryTaskDispatcher(TaskDispatcher):
    def {action}_{resource}(self, resource_id: str, **kwargs) -> None:
        from infrastructure.celery.tasks.{domain} import {action}_{resource}
        {action}_{resource}.delay(resource_id, **kwargs)
```

## 4. Call from Use Case

```python
# In the relevant use case
class SomeUseCase:
    def __init__(self, ..., task_dispatcher: TaskDispatcher):
        self.task_dispatcher = task_dispatcher

    async def execute(self, ...):
        # ... main logic
        # Dispatch background task (non-blocking)
        self.task_dispatcher.{action}_{resource}(str(resource.id))
```

## 5. Register Task Route (if using separate queues)

```python
# In celery config
task_routes = {
    "tasks.{domain}.*": {"queue": "{queue_name}"},
}
```

## 6. Add Periodic Schedule (if needed)

```python
# In celery config beat_schedule
beat_schedule = {
    "{task-name}": {
        "task": "tasks.{domain}.{action}_{resource}",
        "schedule": crontab(hour=0, minute=0),  # Adjust schedule
    },
}
```

## 7. Write Tests

```python
# apps/api/tests/unit/tasks/test_{domain}.py
from unittest.mock import patch, MagicMock

def test_{action}_{resource}_success():
    with patch("infrastructure.celery.tasks.{domain}.do_work") as mock_work:
        mock_work.return_value = expected_result
        result = {action}_{resource}("resource-id-123")
        assert result["status"] == "success"
        mock_work.assert_called_once_with("resource-id-123")

def test_{action}_{resource}_retries_on_failure():
    task = {action}_{resource}
    with patch.object(task, "retry") as mock_retry:
        with patch("...do_work", side_effect=ExternalServiceError):
            task("resource-id-123")
            mock_retry.assert_called_once()
```

## Checklist
- [ ] Task arguments are JSON-serializable (str, int, list, dict only)
- [ ] Task is idempotent (safe to retry)
- [ ] `max_retries` and `time_limit` set
- [ ] Proper error handling and logging
- [ ] Task registered in correct queue
- [ ] TaskDispatcher interface updated
- [ ] CeleryTaskDispatcher implementation updated
- [ ] Called from use case via interface (not direct Celery import)
- [ ] Test written
