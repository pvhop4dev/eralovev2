"""Tests for Trace Context module."""

from infrastructure.trace_context import clear_trace_id, get_trace_id, set_trace_id


class TestTraceContext:
    """Test suite for trace_id context management."""

    def test_set_and_get_trace_id(self):
        tid = set_trace_id("test-trace-123")
        assert tid == "test-trace-123"
        assert get_trace_id() == "test-trace-123"
        clear_trace_id()

    def test_auto_generate_trace_id(self):
        tid = set_trace_id()
        assert len(tid) == 16  # 16-char hex
        assert get_trace_id() == tid
        clear_trace_id()

    def test_clear_trace_id(self):
        set_trace_id("abc")
        clear_trace_id()
        assert get_trace_id() == ""

    def test_default_is_empty(self):
        clear_trace_id()
        assert get_trace_id() == ""

    def test_override_trace_id(self):
        set_trace_id("first")
        set_trace_id("second")
        assert get_trace_id() == "second"
        clear_trace_id()

    def test_incoming_trace_id_preserved(self):
        """Simulate receiving X-Trace-Id from frontend/gateway."""
        incoming = "frontend-trace-42"
        tid = set_trace_id(incoming)
        assert tid == "frontend-trace-42"
        assert get_trace_id() == "frontend-trace-42"
        clear_trace_id()
