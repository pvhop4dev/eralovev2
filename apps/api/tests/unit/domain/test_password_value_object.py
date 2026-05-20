"""Tests for Password Value Object."""

import pytest

from domain.exceptions import ValidationError
from domain.value_objects.password import Password


class TestPasswordValueObject:
    """Test suite for Password value object."""

    def test_create_from_plaintext(self):
        pw = Password.from_plaintext("MyPassword1")
        assert pw.hashed_value != "MyPassword1"
        assert pw.hashed_value.startswith("$2b$")

    def test_verify_correct_password(self):
        pw = Password.from_plaintext("MyPassword1")
        assert pw.verify("MyPassword1") is True

    def test_verify_wrong_password(self):
        pw = Password.from_plaintext("MyPassword1")
        assert pw.verify("WrongPassword1") is False

    def test_from_hash(self):
        original = Password.from_plaintext("MyPassword1")
        restored = Password.from_hash(original.hashed_value)
        assert restored.verify("MyPassword1") is True

    def test_str_representation_hides_password(self):
        pw = Password.from_plaintext("MyPassword1")
        assert str(pw) == "********"
        assert repr(pw) == "Password(***)"

    def test_too_short_raises(self):
        with pytest.raises(ValidationError, match="at least 8"):
            Password.from_plaintext("Short1")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError, match="at most 128"):
            Password.from_plaintext("A1" + "a" * 127)

    def test_no_uppercase_raises(self):
        with pytest.raises(ValidationError, match="uppercase"):
            Password.from_plaintext("alllowercase1")

    def test_no_lowercase_raises(self):
        with pytest.raises(ValidationError, match="lowercase"):
            Password.from_plaintext("ALLUPPERCASE1")

    def test_no_digit_raises(self):
        with pytest.raises(ValidationError, match="digit"):
            Password.from_plaintext("NoDigitsHere")

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            Password.from_plaintext("")

    def test_different_hashes_for_same_password(self):
        """bcrypt should produce different hashes due to random salt."""
        pw1 = Password.from_plaintext("MyPassword1")
        pw2 = Password.from_plaintext("MyPassword1")
        assert pw1.hashed_value != pw2.hashed_value
        # But both should verify
        assert pw1.verify("MyPassword1")
        assert pw2.verify("MyPassword1")
