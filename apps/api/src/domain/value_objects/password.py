"""Password Value Object.

Handles password validation, hashing, and verification.
Uses bcrypt for secure password hashing.
"""

from dataclasses import dataclass

import bcrypt

from domain.exceptions import ValidationError

_MIN_LENGTH = 8
_MAX_LENGTH = 128


@dataclass(frozen=True)
class Password:
    """Immutable password value object.

    Stores the hashed value, never the plaintext.
    Use class methods to create from plaintext or from existing hash.
    """

    hashed_value: str

    @classmethod
    def from_plaintext(cls, plaintext: str) -> "Password":
        """Create a Password from plaintext — validates and hashes.

        Args:
            plaintext: The raw password string from user input.

        Returns:
            Password with bcrypt-hashed value.

        Raises:
            ValidationError: If password doesn't meet requirements.
        """
        cls._validate(plaintext)
        hashed = bcrypt.hashpw(
            plaintext.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        )
        return cls(hashed_value=hashed.decode("utf-8"))

    @classmethod
    def from_hash(cls, hashed: str) -> "Password":
        """Create a Password from an existing hash (e.g., from database).

        No validation is performed — assumes hash is valid.
        """
        return cls(hashed_value=hashed)

    def verify(self, plaintext: str) -> bool:
        """Verify a plaintext password against the stored hash.

        Args:
            plaintext: The raw password to verify.

        Returns:
            True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            self.hashed_value.encode("utf-8"),
        )

    @staticmethod
    def _validate(plaintext: str) -> None:
        """Validate password meets security requirements.

        Rules:
        - At least 8 characters
        - At most 128 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        """
        if not plaintext:
            raise ValidationError("Password cannot be empty")

        if len(plaintext) < _MIN_LENGTH:
            raise ValidationError(f"Password must be at least {_MIN_LENGTH} characters")

        if len(plaintext) > _MAX_LENGTH:
            raise ValidationError(f"Password must be at most {_MAX_LENGTH} characters")

        if not any(c.isupper() for c in plaintext):
            raise ValidationError("Password must contain at least 1 uppercase letter")

        if not any(c.islower() for c in plaintext):
            raise ValidationError("Password must contain at least 1 lowercase letter")

        if not any(c.isdigit() for c in plaintext):
            raise ValidationError("Password must contain at least 1 digit")

    def __str__(self) -> str:
        return "********"

    def __repr__(self) -> str:
        return "Password(***)"
