"""Redis Cache Service.

Provides cache-aside pattern with get_or_set and invalidation.
"""

import json
from collections.abc import Awaitable, Callable
from typing import TypeVar

from redis.asyncio import Redis

T = TypeVar("T")


class CacheService:
    """Redis-based caching service."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> str | None:
        """Get a value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value as string, or None if not found.
        """
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        """Set a value in cache with TTL.

        Args:
            key: Cache key.
            value: Value to cache (string).
            ttl: Time-to-live in seconds (default: 5 minutes).
        """
        await self.redis.setex(key, ttl, value)

    async def get_json(self, key: str) -> dict | list | None:
        """Get a JSON value from cache.

        Args:
            key: Cache key.

        Returns:
            Deserialized JSON value, or None if not found.
        """
        data = await self.redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set_json(self, key: str, value: dict | list, ttl: int = 300) -> None:
        """Set a JSON value in cache.

        Args:
            key: Cache key.
            value: Dict or list to cache.
            ttl: Time-to-live in seconds (default: 5 minutes).
        """
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[dict | list]],
        ttl: int = 300,
    ) -> dict | list:
        """Get from cache, or compute and store.

        Cache-aside pattern: returns cached value if available,
        otherwise calls factory(), caches the result, and returns it.

        Args:
            key: Cache key.
            factory: Async callable that produces the value.
            ttl: Time-to-live in seconds.

        Returns:
            The cached or freshly computed value.
        """
        cached = await self.get_json(key)
        if cached is not None:
            return cached

        value = await factory()
        await self.set_json(key, value, ttl)
        return value

    async def invalidate(self, *keys: str) -> int:
        """Delete one or more cache keys.

        Args:
            keys: Cache keys to delete.

        Returns:
            Number of keys deleted.
        """
        if not keys:
            return 0
        return await self.redis.delete(*keys)

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        WARNING: Uses SCAN (not KEYS) for safety. Use sparingly.

        Args:
            pattern: Glob pattern (e.g., "eralove:couple:123:*").

        Returns:
            Number of keys deleted.
        """
        keys: list[str] = []
        async for key in self.redis.scan_iter(match=pattern, count=100):
            keys.append(key)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return bool(await self.redis.exists(key))

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key in seconds."""
        return await self.redis.ttl(key)
