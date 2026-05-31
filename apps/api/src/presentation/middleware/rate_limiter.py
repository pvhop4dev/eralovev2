"""Rate Limiter Dependency using Redis."""

import time
import uuid
import structlog
from fastapi import Request

from domain.exceptions import TooManyRequestsError
from presentation.deps import RedisClient

logger = structlog.get_logger()


class RateLimiter:
    """FastAPI dependency for rate limiting using a Redis sliding window log."""

    def __init__(self, requests: int, window_seconds: int) -> None:
        """Initialize the rate limiter.

        Args:
            requests: Maximum number of requests allowed in the window.
            window_seconds: The duration of the window in seconds.
        """
        self.requests = requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request, redis: RedisClient) -> None:
        """Execute the rate limit check.

        Args:
            request: The FastAPI Request.
            redis: The Redis client.

        Raises:
            TooManyRequestsError: If client has exceeded the limit.
        """
        # Determine client identifier (use IP or proxy forward IP)
        ip = "unknown"
        if request.client:
            ip = request.client.host
        # Support X-Forwarded-For if behind a proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()

        path = request.url.path
        key = f"eralove:ratelimit:{ip}:{path}"

        now = time.time()
        clear_before = now - self.window_seconds
        member = f"{now}:{uuid.uuid4()}"

        try:
            async with redis.pipeline(transaction=True) as pipe:
                # 1. Clean log of requests older than window_seconds
                pipe.zremrangebyscore(key, 0, clear_before)
                # 2. Count requests in this window
                pipe.zcard(key)
                # 3. Add current request
                pipe.zadd(key, {member: now})
                # 4. Set expiration on key to clean up Redis memory
                pipe.expire(key, self.window_seconds)
                
                results = await pipe.execute()
                
            # results[1] is the result of ZCARD before we added the new request
            request_count = results[1]

            if request_count >= self.requests:
                logger.warning(
                    "rate_limit_exceeded",
                    ip=ip,
                    path=path,
                    requests=self.requests,
                    count=request_count + 1
                )
                raise TooManyRequestsError(
                    f"Rate limit exceeded. Maximum {self.requests} requests per {self.window_seconds} seconds."
                )
        except TooManyRequestsError:
            raise
        except Exception as e:
            # Fallback: don't block API requests if Redis rate limiting fails, just log it
            logger.error("rate_limiter_failed", error=str(e))
