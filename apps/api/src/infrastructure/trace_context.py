"""Trace Context — Request-scoped trace ID using contextvars.

Provides a trace_id that flows through the entire request lifecycle:
  Request → Middleware → Route → Use Case → Repository → Response Header

Usage:
    from infrastructure.trace_context import get_trace_id, set_trace_id

    # In middleware: set at start of request
    set_trace_id("abc-123")

    # Anywhere in the request lifecycle: read
    trace_id = get_trace_id()

    # In structlog: automatically bound via middleware
    logger.info("action", trace_id=get_trace_id())
"""

import uuid
from contextvars import ContextVar

# Context variable — isolated per async task / request
_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def set_trace_id(trace_id: str | None = None) -> str:
    """Set the trace ID for the current request.

    Args:
        trace_id: Optional trace ID. If None, generates a new UUID.

    Returns:
        The trace ID that was set.
    """
    tid = trace_id or uuid.uuid4().hex[:16]
    _trace_id_var.set(tid)
    return tid


def get_trace_id() -> str:
    """Get the trace ID for the current request.

    Returns:
        The current trace ID, or empty string if not set.
    """
    return _trace_id_var.get()


def clear_trace_id() -> None:
    """Clear the trace ID (end of request cleanup)."""
    _trace_id_var.set("")
