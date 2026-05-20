"""Tests for Email Value Object."""

import pytest

from domain.exceptions import ValidationError
from domain.value_objects.email import Email


class TestEmailValueObject:
    """Test suite for Email value object."""

    def test_valid_email(self):
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_normalizes_to_lowercase(self):
        email = Email("Test@EXAMPLE.Com")
        assert email.value == "test@example.com"

    def test_strips_whitespace(self):
        email = Email("  test@example.com  ")
        assert email.value == "test@example.com"

    def test_domain_property(self):
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_local_part_property(self):
        email = Email("user@example.com")
        assert email.local_part == "user"

    def test_equality_with_email(self):
        email1 = Email("test@example.com")
        email2 = Email("TEST@example.com")
        assert email1 == email2

    def test_equality_with_string(self):
        email = Email("test@example.com")
        assert email == "test@example.com"

    def test_hash_consistent(self):
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        assert hash(email1) == hash(email2)

    def test_str_representation(self):
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_empty_email_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            Email("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            Email("   ")

    def test_invalid_format_no_at(self):
        with pytest.raises(ValidationError, match="Invalid email"):
            Email("notanemail")

    def test_invalid_format_no_domain(self):
        with pytest.raises(ValidationError, match="Invalid email"):
            Email("user@")

    def test_invalid_format_no_tld(self):
        with pytest.raises(ValidationError, match="Invalid email"):
            Email("user@domain")

    def test_too_long_email_raises(self):
        long_local = "a" * 250
        with pytest.raises(ValidationError, match="255"):
            Email(f"{long_local}@example.com")

    def test_immutable(self):
        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email.value = "other@example.com"  # type: ignore

    def test_complex_valid_emails(self):
        """Test various valid email formats."""
        valid_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user@sub.domain.com",
            "user123@example.co.uk",
        ]
        for addr in valid_emails:
            email = Email(addr)
            assert email.value == addr.lower()
