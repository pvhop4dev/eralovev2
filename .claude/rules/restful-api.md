---
name: restful-api
description: RESTful API design rules — HTTP methods, status codes, URL patterns, error handling, pagination
---

# RESTful API Rules

## URL Design

### Pattern

```
https://api-love.eraquix.com/api/v1/{resource}
https://api-love.eraquix.com/api/v1/{resource}/{id}
https://api-love.eraquix.com/api/v1/{resource}/{id}/{sub-resource}
```

### Naming Rules

- Resources are **nouns**, plural: `/events`, `/photos`, `/messages`
- NEVER use verbs in URLs: `/getEvents` WRONG, `/events` CORRECT
- Kebab-case for multi-word resources: `/match-requests`, `/shared-notes`, `/time-capsules`
- Nested resources max 2 levels: `/events/{id}/photos` OK, `/couples/{id}/events/{id}/photos` TOO DEEP
- Use query params for filtering, NOT path segments: `/events?type=birthday` NOT `/events/birthday`

### URL Examples

```
GET    /api/v1/events                    # List events
POST   /api/v1/events                    # Create event
GET    /api/v1/events/{id}               # Get single event
PATCH  /api/v1/events/{id}               # Partial update event
DELETE /api/v1/events/{id}               # Soft delete event
POST   /api/v1/events/{id}/restore       # Restore deleted event
GET    /api/v1/events/{id}/photos        # List photos for event

GET    /api/v1/messages                  # List messages
POST   /api/v1/messages                  # Send message
POST   /api/v1/messages/{id}/pin         # Pin message (action)
POST   /api/v1/messages/{id}/react       # React to message (action)

POST   /api/v1/auth/login                # Auth action
POST   /api/v1/auth/register             # Auth action
POST   /api/v1/auth/refresh              # Auth action

POST   /api/v1/match/request             # Send match request
POST   /api/v1/match/requests/{id}/accept   # Accept match
POST   /api/v1/match/requests/{id}/decline  # Decline match
```

### Action Endpoints (exceptions to pure REST)

For operations that don't map cleanly to CRUD, use `POST /resource/{id}/action`:

```
POST /events/{id}/restore      # Restore soft-deleted event
POST /messages/{id}/pin        # Toggle pin
POST /messages/{id}/react      # Add reaction
POST /messages/{id}/reveal     # Reveal secret message
POST /couple/pause             # Pause relationship
POST /couple/resume            # Resume relationship
POST /ari/daily-checkin        # Submit mood check-in
POST /notifications/read-all   # Mark all as read
```

---

## HTTP Methods

| Method   | Purpose                          | Idempotent | Request Body  | Response                     |
| -------- | -------------------------------- | ---------- | ------------- | ---------------------------- |
| `GET`    | Read resource(s)                 | Yes        | No            | 200 + data                   |
| `POST`   | Create resource / Trigger action | No         | Yes           | 201 (create) or 200 (action) |
| `PATCH`  | Partial update                   | No         | Yes (partial) | 200 + updated data           |
| `DELETE` | Delete resource (soft)           | Yes        | No            | 204 No Content               |

### NEVER use:

- `PUT` — We always do partial updates with `PATCH`. PUT implies full replacement which is error-prone.
- `GET` with request body
- `DELETE` with required request body (use query params if needed: `DELETE /messages/{id}?for=both`)

---

## HTTP Status Codes

### Success

| Code             | When                                                 |
| ---------------- | ---------------------------------------------------- |
| `200 OK`         | GET, PATCH, action POST (login, pin, react)          |
| `201 Created`    | POST that creates a resource (event, message, photo) |
| `202 Accepted`   | Async job started (data export, photo processing)    |
| `204 No Content` | DELETE, or action with no response body              |

### Client Errors

| Code                       | When                                          | Error Code            |
| -------------------------- | --------------------------------------------- | --------------------- |
| `400 Bad Request`          | Invalid input, validation failure             | `VALIDATION_ERROR`    |
| `401 Unauthorized`         | Missing/expired/invalid JWT                   | `UNAUTHORIZED`        |
| `403 Forbidden`            | Valid JWT but no permission (not your couple) | `FORBIDDEN`           |
| `404 Not Found`            | Resource doesn't exist or is soft-deleted     | `NOT_FOUND`           |
| `409 Conflict`             | Duplicate (email taken, already matched)      | `CONFLICT`            |
| `422 Unprocessable Entity` | Valid JSON but business rule violation        | `BUSINESS_RULE_ERROR` |
| `429 Too Many Requests`    | Rate limit exceeded                           | `RATE_LIMITED`        |

### Server Errors

| Code                        | When                                      |
| --------------------------- | ----------------------------------------- |
| `500 Internal Server Error` | Unhandled exception (log + alert)         |
| `502 Bad Gateway`           | External API failure (weather, Claude AI) |
| `503 Service Unavailable`   | Database/Redis down                       |

---

## Response Format

### Unified Response Wrapper

```python
# apps/api/src/presentation/schemas/response.py
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    cursor: str | None = None
    has_next: bool = False

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None         # For validation errors
    details: list[dict] | None = None

class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: PaginationMeta | None = None
    error: ErrorDetail | None = None
```

### Success Response Examples

```json
// GET /api/v1/events/{id} → 200
{
  "data": {
    "id": "01234567-89ab-cdef-0123-456789abcdef",
    "title": "Date Night",
    "event_type": "date",
    "event_date": "2026-05-01",
    "created_at": "2026-04-20T10:30:00Z"
  },
  "meta": null,
  "error": null
}

// GET /api/v1/events?month=2026-05 → 200
{
  "data": [
    { "id": "...", "title": "Date Night", ... },
    { "id": "...", "title": "Birthday", ... }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "has_next": true
  },
  "error": null
}

// POST /api/v1/events → 201
{
  "data": { "id": "...", "title": "New Event", ... },
  "meta": null,
  "error": null
}

// DELETE /api/v1/events/{id} → 204
// (no body)
```

### Error Response Examples

**IMPORTANT**: All error responses include `trace_id` in `meta` for request correlation.
The `X-Trace-Id` response header is also set for every response (success or error).

```json
// 400 — Validation Error
{
  "data": null,
  "meta": { "trace_id": "a1b2c3d4e5f67890" },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "event_date", "message": "Date must be in YYYY-MM-DD format" },
      { "field": "title", "message": "Title is required" }
    ]
  }
}

// 401 — Unauthorized
{
  "data": null,
  "meta": { "trace_id": "a1b2c3d4e5f67890" },
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Access token expired"
  }
}

// 404 — Not Found
{
  "data": null,
  "meta": { "trace_id": "a1b2c3d4e5f67890" },
  "error": {
    "code": "NOT_FOUND",
    "message": "Event not found"
  }
}

// 409 — Conflict
{
  "data": null,
  "meta": { "trace_id": "a1b2c3d4e5f67890" },
  "error": {
    "code": "CONFLICT",
    "message": "Email is already registered"
  }
}

// 422 — Business Rule
{
  "data": null,
  "meta": { "trace_id": "a1b2c3d4e5f67890" },
  "error": {
    "code": "BUSINESS_RULE_ERROR",
    "message": "You can only match with one person at a time"
  }
}

// 429 — Rate Limited
{
  "data": null,
  "meta": null,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Try again in 45 seconds.",
    "details": [{ "retry_after": 45 }]
  }
}
```

---

## Error Handling Architecture

### Domain Exceptions → HTTP Status Mapping

```python
# apps/api/src/domain/exceptions.py
class DomainError(Exception):
    """Base for all domain errors."""

class NotFoundError(DomainError):
    """Entity not found."""

class ConflictError(DomainError):
    """Duplicate resource."""

class ForbiddenError(DomainError):
    """No permission for this resource."""

class BusinessRuleError(DomainError):
    """Business logic violation."""

class AlreadyDeletedError(DomainError):
    """Soft-deleted entity cannot be deleted again."""

class RestoreWindowExpiredError(DomainError):
    """Cannot restore after window expires."""
```

```python
# apps/api/src/presentation/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

EXCEPTION_STATUS_MAP = {
    NotFoundError: 404,
    ConflictError: 409,
    ForbiddenError: 403,
    BusinessRuleError: 422,
    AlreadyDeletedError: 422,
    RestoreWindowExpiredError: 422,
}

async def domain_exception_handler(request: Request, exc: DomainError):
    status = EXCEPTION_STATUS_MAP.get(type(exc), 500)
    code = type(exc).__name__.replace("Error", "").upper()
    return JSONResponse(
        status_code=status,
        content={
            "data": None,
            "meta": None,
            "error": {
                "code": code,
                "message": str(exc),
            },
        },
    )
```

---

## Pagination

### Offset-based (for calendar, search, admin)

```
GET /api/v1/events?page=2&per_page=20&month=2026-05
```

Response meta:

```json
{ "page": 2, "per_page": 20, "total": 45, "has_next": true }
```

### Cursor-based (for chat messages, feed)

```
GET /api/v1/messages?cursor=eyJjcmVhdGVkX2F0IjoiMjAy...&limit=50
```

Response meta:

```json
{ "cursor": "eyJjcmVhdGVkX2F0IjoiMjAy...", "has_next": true }
```

### Rules

- Default `per_page` = 20, max = 100
- Default `limit` (cursor) = 50, max = 100
- Chat messages: cursor-based, sorted by `created_at DESC`
- Events, photos, notifications: offset-based
- Always include `has_next` boolean
- Cursor is opaque base64-encoded JSON (client must not decode)

---

## Query Parameters

### Filtering

```
GET /events?type=birthday&date_from=2026-01-01&date_to=2026-12-31
GET /photos?event_id=xxx&date_from=2026-01-01
GET /messages?pinned=true
GET /notifications?unread_only=true
```

### Sorting

```
GET /events?sort=event_date&order=asc
GET /photos?sort=created_at&order=desc
```

Default sort: `created_at DESC` for most resources.

### Searching

```
GET /users/search?q=john
GET /events?q=birthday
```

---

## Versioning

- URL-based versioning: `/api/v1/`, `/api/v2/`
- Start with `v1`, increment on breaking changes
- Breaking changes: removing fields, changing types, changing URL structure
- Non-breaking: adding optional fields, adding new endpoints

## Content Type

- Request: `Content-Type: application/json`
- Response: `Content-Type: application/json; charset=utf-8`
- File upload: presigned URL (not multipart through API)

## Date/Time Format

- All dates in API: ISO 8601 (`2026-05-01`)
- All datetimes in API: ISO 8601 with timezone (`2026-05-01T10:30:00Z`)
- Store in UTC, display in user's timezone (frontend responsibility)
- Date-only fields (event_date, date_of_birth): `YYYY-MM-DD` string

## Idempotency

- POST create operations should check for duplicates (email, username)
- Use `Idempotency-Key` header for payment/critical operations (future)
- DELETE is idempotent — deleting already-deleted returns 204 (not 404)

## HATEOAS (NOT used)

We do NOT use HATEOAS links. Frontend knows the API structure. Keep responses simple.
