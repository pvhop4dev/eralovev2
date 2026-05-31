"""Pytest configuration and shared fixtures."""

import datetime
import sys

# Patch UTC timezone for Python versions < 3.11 (e.g. Python 3.10)
if not hasattr(datetime, "UTC"):
    datetime.UTC = datetime.timezone.utc  # noqa: UP017

from pathlib import Path

# Add src/ to path so tests can import from domain, application, etc.
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / ".." / "src"))
