---
name: observability
description: Trace ID, structured logging, and request observability rules
---

# Observability Rules

## Trace ID — Request Tracing

### Architecture

Every HTTP request gets a unique `trace_id` that flows through the entire stack:

```
Frontend → X-Trace-Id header → TraceMiddleware → contextvars →
  Route → Use Case → Repository → Database
  → Response Header (X-Trace-Id) → Frontend DevTools
```

### Implementation Files

- `infrastructure/trace_context.py` — `contextvars` storage
- `presentation/middleware/trace_middleware.py` — ASGI middleware
- `presentation/middleware/error_handler.py` — trace_id in error responses

### Usage Patterns

#### Reading trace_id anywhere in the request lifecycle

```python
from infrastructure.trace_context import get_trace_id

# In use case, repository, service, etc.
trace_id = get_trace_id()
logger.info("action", trace_id=trace_id)
```

#### Automatic structlog binding (already done by middleware)

```python
import structlog
logger = structlog.get_logger()

# trace_id is automatically included in log output
logger.info("user_login", user_id=str(user.id))
# Output: {"event": "user_login", "user_id": "...", "trace_id": "abc123", "method": "POST", "path": "/api/v1/auth/login"}
```

#### Frontend reading trace_id from response

```typescript
const res = await fetch("/api/v1/endpoint");
const traceId = res.headers.get("X-Trace-Id");

// Log error with trace_id for support correlation
if (!res.ok) {
  console.error(`API Error [trace: ${traceId}]`, await res.json());
}
```

#### Forwarding trace_id between services (distributed tracing)

```typescript
// Frontend sends trace_id to a different backend
const traceId = crypto.randomUUID().replace(/-/g, "").slice(0, 16);
const res = await fetch("/api/v1/endpoint", {
  headers: { "X-Trace-Id": traceId },
});
```

### Rules

1. **NEVER** remove or modify `TraceMiddleware` — it's the foundation of observability
2. **ALWAYS** include `trace_id` in error responses via `meta.trace_id`
3. **ALWAYS** expose `X-Trace-Id` in CORS (`expose_headers=["X-Trace-Id"]`)
4. **ALWAYS** use `get_trace_id()` from `infrastructure.trace_context` — NOT custom context passing
5. **NEVER** log trace_id manually in structlog — it's auto-bound by middleware
6. When creating new error handlers, include `meta.trace_id` pattern:

   ```python
   from infrastructure.trace_context import get_trace_id

   return JSONResponse(
       status_code=status,
       content={
           "data": None,
           "meta": {"trace_id": get_trace_id()} if get_trace_id() else None,
           "error": {"code": "...", "message": "..."},
       },
   )
   ```

## Structured Logging

### Log Format

All logs use structlog with JSON output:

```python
import structlog
logger = structlog.get_logger()

# CORRECT — structured key-value pairs
logger.info("event_created", event_id=str(event.id), user_id=str(user.id))

# WRONG — unstructured string interpolation
logger.info(f"Event {event.id} created by {user.id}")
```

### What to Log

| Event                  | Level   | Fields                                           |
| ---------------------- | ------- | ------------------------------------------------ |
| Request completed      | INFO    | trace_id, method, path, status_code, duration_ms |
| Auth success/fail      | INFO    | user_id, action                                  |
| Domain error           | WARNING | trace_id, error_code, message                    |
| Unexpected error       | ERROR   | trace_id, exception, stack_trace                 |
| DB query slow (>500ms) | WARNING | query, duration_ms                               |

### What NOT to Log

- Passwords, tokens, API keys
- Personal message content
- Full request/response bodies (log summary instead)
- PII beyond user_id
