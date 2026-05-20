"""Redis Client.

Async Redis connection for caching, pub/sub, and sessions.
"""

from redis.asyncio import ConnectionPool, Redis

from infrastructure.config import get_settings

settings = get_settings()

_pool: ConnectionPool | None = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create the Redis connection pool."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=True,
        )
    return _pool


async def get_redis() -> Redis:
    """Get a Redis client from the connection pool.

    Usage with FastAPI Depends:
        redis: Annotated[Redis, Depends(get_redis)]
    """
    pool = await get_redis_pool()
    return Redis(connection_pool=pool)


async def close_redis_pool() -> None:
    """Close the Redis connection pool — call on shutdown."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
