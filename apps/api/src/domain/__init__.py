"""Domain package."""

import datetime

# Patch UTC timezone for Python versions < 3.11 (e.g. Python 3.10)
if not hasattr(datetime, "UTC"):
    datetime.UTC = datetime.timezone.utc  # noqa: UP017
