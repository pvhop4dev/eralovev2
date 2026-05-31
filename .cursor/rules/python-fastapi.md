---
name: python-fastapi
description: Python and FastAPI specific coding patterns, async rules, middleware, and configuration
---

# Python & FastAPI Rules

## Project Setup

### Python Version & Dependencies

- Python 3.12+ required
- Use `pyproject.toml` (PEP 621) for dependency management
- Use `uv` or `pip-tools` for locking dependencies
- Virtual environment: `.venv/` (never commit)
- Linting: `ruff` (replaces flake8, isort, black)
- Type checking: `mypy` with strict mode

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "ASYNC", "B", "SIM", "RUF"]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"
```

## Async/Await Rules

### ALWAYS async for I/O

```python
# CORRECT — async for all I/O
async def get_user(user_id: UUID) -> User:
    result = await self.session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    return result.scalar_one_or_none()

# WRONG — sync I/O blocks the event loop
def get_user(user_id: UUID) -> User:
    result = self.session.execute(...)  # BLOCKS!
```

### Use `asyncio.gather` for Parallel I/O

```python
# CORRECT — parallel requests
async def get_dashboard_data(couple_id: UUID) -> DashboardData:
    events, photos, weather = await asyncio.gather(
        self.event_repo.get_recent(couple_id),
        self.photo_repo.get_latest(couple_id, limit=5),
        self.weather_service.get_current(couple_id),
    )
    return DashboardData(events=events, photos=photos, weather=weather)

# WRONG — sequential (2-3x slower)
async def get_dashboard_data(couple_id: UUID) -> DashboardData:
    events = await self.event_repo.get_recent(couple_id)
    photos = await self.photo_repo.get_latest(couple_id, limit=5)
    weather = await self.weather_service.get_current(couple_id)
```

### Never Block the Event Loop

```python
# WRONG — CPU-heavy task blocks event loop
async def process_image(image: bytes) -> bytes:
    return heavy_resize(image)  # Blocks!

# CORRECT — offload to thread pool
async def process_image(image: bytes) -> bytes:
    return await asyncio.to_thread(heavy_resize, image)

# BETTER — offload to Celery task (see celery-rules.md)
```

## FastAPI Application Setup

### Lifespan Pattern (NOT @app.on_event)

```python
# CORRECT — modern lifespan pattern
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize connections
    await init_db()
    redis_pool = await create_redis_pool()
    app.state.redis = redis_pool
    yield
    # Shutdown: cleanup
    await redis_pool.aclose()
    await dispose_db_engine()

app = FastAPI(
    title="Eralove API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# WRONG — deprecated pattern
@app.on_event("startup")  # DEPRECATED in FastAPI 0.109+
async def startup():
    ...
```

### Middleware Order (matters!)

```python
# Register in REVERSE order (last registered = first executed)
# TraceMiddleware must run BEFORE CORS to set trace_id for all requests.
app.add_middleware(TraceMiddleware)  # trace_id + structlog binding
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Trace-Id"],  # Allow frontend to read trace header
)
app.add_middleware(RateLimitMiddleware)
```

### Dependency Injection — Deep Pattern

```python
# deps.py — shared dependencies
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    payload = verify_jwt(token)
    user = await UserRepository(session).get_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user

async def get_current_couple(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Couple:
    couple = await CoupleRepository(session).get_by_user(user.id)
    if not couple:
        raise CoupleNotFoundError("You are not matched with anyone")
    return couple

# Type aliases for clean route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentCouple = Annotated[Couple, Depends(get_current_couple)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
```

## Configuration Management

### Settings Pattern (Pydantic Settings)

```python
# apps/api/src/infrastructure/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Eralove API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AWS S3
    AWS_S3_BUCKET: str = "eralove-media"
    AWS_REGION: str = "ap-southeast-1"
    S3_PRESIGN_EXPIRY: int = 3600

    # Claude AI
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "case_sensitive": True}

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Logging

### Structured Logging (structlog)

```python
import structlog

logger = structlog.get_logger()

# In use cases / services — trace_id auto-bound by TraceMiddleware
async def execute(self, dto: CreateEventRequest, user_id: UUID) -> EventResponse:
    logger.info("creating_event", user_id=str(user_id), title=dto.title)
    try:
        event = await self.repo.create(...)
        logger.info("event_created", event_id=str(event.id))
        return EventResponse.model_validate(event)
    except Exception as e:
        logger.error("event_creation_failed", error=str(e), user_id=str(user_id))
        raise

# To access trace_id manually:
from infrastructure.trace_context import get_trace_id
trace_id = get_trace_id()  # available in any layer during request
```

### Logging Rules

- **NEVER** log sensitive data: passwords, tokens, API keys, personal messages
- **ALWAYS** log: user_id, couple_id, action, result (success/failure)
- Use structured key-value pairs, not f-strings
- Log levels: DEBUG (dev only), INFO (business events), WARNING (recoverable), ERROR (failures)

## Pydantic V2 Patterns

### Request/Response Schema

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from uuid import UUID

class CreateEventRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., pattern="^(date|birthday|anniversary|custom)$")
    event_date: date
    location: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)
    metadata: dict | None = None

    @field_validator("event_date")
    @classmethod
    def date_not_too_far(cls, v: date) -> date:
        if v.year > datetime.now().year + 10:
            raise ValueError("Event date too far in the future")
        return v

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    event_type: str
    event_date: date
    created_at: datetime
```

### Common Validators

```python
# Reusable validators
from pydantic import field_validator
import re

class HasDisplayName(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)

    @field_validator("display_name")
    @classmethod
    def clean_display_name(cls, v: str) -> str:
        return re.sub(r"\s+", " ", v.strip())
```

## File Structure Standards

```
apps/api/src/
├── domain/
│   ├── entities/          # One file per entity
│   ├── value_objects/     # Email, Password, Coordinates, etc.
│   ├── repositories/      # Abstract base classes
│   ├── services/          # Domain services (cross-entity logic)
│   ├── events/            # Domain events
│   └── exceptions.py      # All domain exceptions
├── application/
│   ├── use_cases/         # Grouped by feature
│   │   ├── auth/
│   │   ├── calendar/
│   │   ├── chat/
│   │   └── ...
│   ├── dtos/              # Pydantic request/response schemas
│   ├── services/          # Application service interfaces
│   └── interfaces/        # External service interfaces (S3, AI, email)
├── infrastructure/
│   ├── config.py          # Settings
│   ├── trace_context.py   # Request-scoped trace_id (contextvars)
│   ├── database/
│   │   ├── connection.py  # Engine, session factory
│   │   ├── models/        # SQLAlchemy models
│   │   ├── repositories/  # Concrete repository implementations
│   │   └── mixins.py      # SoftDeleteMixin, TimestampMixin
│   ├── redis/
│   │   ├── client.py      # Redis connection
│   │   └── cache.py       # Cache service
│   ├── quotes/
│   │   └── love_quotes.py # Daily love quotes (50+)
│   ├── s3/
│   │   └── client.py      # S3 presigned URL generation
│   ├── ai/
│   │   └── claude_client.py
│   └── external/
│       ├── weather.py
│       └── mapbox.py
└── presentation/
    ├── main.py            # FastAPI app + lifespan + middleware
    ├── api/
    │   └── v1/            # All route files
    ├── middleware/
    │   ├── auth_middleware.py
    │   ├── error_handler.py
    │   ├── trace_middleware.py  # X-Trace-Id + structlog binding
    │   └── rate_limit.py
    ├── deps.py            # Shared FastAPI dependencies
    └── schemas/
        └── response.py    # ApiResponse wrapper
```
