"""Shared FastAPI Dependencies.

Dependency injection providers for routes.
"""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import get_session
from infrastructure.redis.client import get_redis

# ── Type aliases for clean route signatures ──────────────
DbSession = Annotated[AsyncSession, Depends(get_session)]
RedisClient = Annotated[Redis, Depends(get_redis)]
