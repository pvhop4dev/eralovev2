"""Eralove API — FastAPI Application Entry Point.

This is the main FastAPI application with:
- Lifespan (startup/shutdown)
- CORS middleware
- Exception handlers
- API router registration
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from domain.exceptions import DomainError
from infrastructure.config import get_settings
from infrastructure.database.connection import dispose_db_engine
from infrastructure.redis.client import close_redis_pool
from presentation.api.v1.health import router as health_router
from presentation.middleware.error_handler import (
    domain_exception_handler,
    validation_exception_handler,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown events."""
    # ── Startup ──────────────────────────────
    # Database and Redis connections are lazy-initialized
    # Nothing to do here for now
    yield
    # ── Shutdown ─────────────────────────────
    await dispose_db_engine()
    await close_redis_pool()


# ── Create FastAPI App ───────────────────────────────────
app = FastAPI(
    title="Eralove API",
    description="Nơi lưu giữ mọi khoảnh khắc yêu thương 💗",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
    openapi_url="/openapi.json" if settings.is_dev else None,
)

# ── Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ──────────────────────────────────
app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

# ── Routers ─────────────────────────────────────────────
app.include_router(health_router, prefix="/api/v1")

# Future routers will be added here:
# app.include_router(auth_router, prefix="/api/v1")
# app.include_router(match_router, prefix="/api/v1")
# app.include_router(events_router, prefix="/api/v1")
# app.include_router(messages_router, prefix="/api/v1")
