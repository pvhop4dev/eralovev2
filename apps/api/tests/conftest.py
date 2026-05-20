"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src/ to path so tests can import from domain, application, etc.
sys.path.insert(0, str(Path(__file__).resolve().parents[0] / ".." / "src"))
