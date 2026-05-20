"""Email Value Object.

Encapsulates email validation and normalization.
Domain layer — no external dependencies.
"""

import re
from dataclasses import dataclass

from domain.exceptions import ValidationError

# RFC 5322 simplified pattern
_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
)


@dataclass(frozen=True)
class Email:
    """Immutable email value object with validation and normalization."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("Email cannot be empty")

        normalized = self.value.strip().lower()

        if len(normalized) > 255:
            raise ValidationError("Email must be at most 255 characters")

        if not _EMAIL_PATTERN.match(normalized):
            raise ValidationError(f"Invalid email format: {self.value}")

        # Use object.__setattr__ since dataclass is frozen
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def domain(self) -> str:
        """Return the domain part of the email."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Return the local part (before @) of the email."""
        return self.value.split("@")[0]
