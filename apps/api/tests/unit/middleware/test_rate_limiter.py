"""Tests for Rate Limiter Dependency."""

from unittest.mock import MagicMock

import pytest

from domain.exceptions import TooManyRequestsError
from presentation.middleware.rate_limiter import RateLimiter


class MockPipeline:
    """Mock Redis Pipeline for transaction execution."""

    def __init__(self, zcard_value: int, raises_error: bool = False) -> None:
        self.zcard_value = zcard_value
        self.raises_error = raises_error
        self.zremrangebyscore = MagicMock()
        self.zcard = MagicMock()
        self.zadd = MagicMock()
        self.expire = MagicMock()

    async def __aenter__(self) -> "MockPipeline":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def execute(self) -> list:
        if self.raises_error:
            raise Exception("Redis connection error")
        # Return [zremrangebyscore_res, zcard_res, zadd_res, expire_res]
        # results[1] is the ZCARD result (number of requests before current one)
        return [0, self.zcard_value, 1, True]


class TestRateLimiter:
    """Test suite for RateLimiter dependency."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests(self):
        """Test that requests within limits are allowed."""
        # 5 requests allowed in 60s
        limiter = RateLimiter(requests=5, window_seconds=60)
        
        # Mock request and redis
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.url.path = "/api/v1/auth/login"

        redis = MagicMock()
        # Mock pipeline returning 3 existing requests (within 5 requests limit)
        redis.pipeline.return_value = MockPipeline(zcard_value=3)

        # Calling the limiter should not raise any exceptions
        await limiter(request, redis)
        
        # Verify pipeline execution
        redis.pipeline.assert_called_once_with(transaction=True)

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_on_excessive_requests(self):
        """Test that requests exceeding limits are blocked."""
        # 5 requests allowed in 60s
        limiter = RateLimiter(requests=5, window_seconds=60)
        
        # Mock request and redis
        request = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.url.path = "/api/v1/auth/register"

        redis = MagicMock()
        # Mock pipeline returning 5 existing requests (reaches the 5 requests limit)
        redis.pipeline.return_value = MockPipeline(zcard_value=5)

        with pytest.raises(TooManyRequestsError) as exc_info:
            await limiter(request, redis)
            
        assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limiter_fail_open_on_redis_error(self):
        """Test that rate limiter fails open (allows request) if Redis errors."""
        limiter = RateLimiter(requests=5, window_seconds=60)
        
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.url.path = "/api/v1/auth/login"

        redis = MagicMock()
        # Mock pipeline throwing an error
        redis.pipeline.return_value = MockPipeline(zcard_value=0, raises_error=True)

        # Rate limiter should NOT raise TooManyRequestsError when redis fails (fail-open)
        await limiter(request, redis)
        
        redis.pipeline.assert_called_once_with(transaction=True)

    @pytest.mark.asyncio
    async def test_rate_limiter_respects_x_forwarded_for(self):
        """Test that rate limiter uses X-Forwarded-For IP if present."""
        limiter = RateLimiter(requests=5, window_seconds=60)
        
        request = MagicMock()
        request.client.host = "127.0.0.1"  # Proxy IP
        # X-Forwarded-For header containing the real client IP
        request.headers = {"x-forwarded-for": "203.0.113.195, 70.41.3.18"}
        request.url.path = "/api/v1/auth/login"

        redis = MagicMock()
        pipeline = MockPipeline(zcard_value=0)
        redis.pipeline.return_value = pipeline

        await limiter(request, redis)
        
        # Extract the key used in pipeline commands to verify the IP used is the real client IP
        pipeline_mock_zadd = pipeline.zadd
        called_key = pipeline_mock_zadd.call_args[0][0]
        
        assert "203.0.113.195" in called_key
        assert "127.0.0.1" not in called_key
