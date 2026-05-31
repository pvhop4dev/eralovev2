"""Trace Middleware — Generates and propagates trace_id per request.

Flow:
  1. Check incoming request for `X-Trace-Id` header (to support distributed tracing)
  2. If not present, generate a new trace_id (16-char hex)
  3. Store in contextvars (accessible anywhere in the request)
  4. Bind to structlog for all log messages
  5. Set `X-Trace-Id` response header

This enables full request traceability:
  Frontend → API Gateway → Backend → Database → Response Header → Frontend DevTools
"""

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from infrastructure.trace_context import clear_trace_id, set_trace_id

logger = structlog.get_logger()

# Response header name
TRACE_HEADER = "X-Trace-Id"


class TraceMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that assigns a trace_id to every request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 1. Get or generate trace_id
        incoming_trace = request.headers.get(TRACE_HEADER)
        trace_id = set_trace_id(incoming_trace)

        # 2. Bind trace_id to structlog for this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            method=request.method,
            path=request.url.path,
        )

        # 3. Track request timing
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            # Re-raise — exception handlers will catch it
            # But still set the trace header on error responses
            raise
        finally:
            # Calculate duration
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "request_completed",
                status_code=getattr(response, "status_code", 500) if "response" in dir() else 500,
                duration_ms=duration_ms,
            )
            # Cleanup context
            clear_trace_id()
            structlog.contextvars.clear_contextvars()

        # 4. Set trace_id in response header
        response.headers[TRACE_HEADER] = trace_id

        return response
