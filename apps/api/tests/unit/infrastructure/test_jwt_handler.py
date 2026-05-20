"""Tests for JWT Token Handler."""

from uuid import uuid4

import pytest

from domain.exceptions import InvalidTokenError, TokenExpiredError
from infrastructure.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token,
)


class TestJWTHandler:
    """Test suite for JWT handler."""

    def test_create_access_token(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        user_id = uuid4()
        token = create_refresh_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_refresh_token(self):
        user_id = uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token, expected_type="refresh")
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_get_user_id_from_access_token(self):
        user_id = uuid4()
        token = create_access_token(user_id)
        extracted_id = get_user_id_from_token(token, expected_type="access")
        assert extracted_id == user_id

    def test_get_user_id_from_refresh_token(self):
        user_id = uuid4()
        token = create_refresh_token(user_id)
        extracted_id = get_user_id_from_token(token, expected_type="refresh")
        assert extracted_id == user_id

    def test_wrong_token_type_raises(self):
        user_id = uuid4()
        access_token = create_access_token(user_id)
        with pytest.raises(InvalidTokenError, match="Expected refresh"):
            decode_token(access_token, expected_type="refresh")

    def test_invalid_token_string_raises(self):
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            decode_token("not-a-valid-token")

    def test_empty_token_raises(self):
        with pytest.raises(InvalidTokenError):
            decode_token("")

    def test_different_users_get_different_tokens(self):
        user1 = uuid4()
        user2 = uuid4()
        token1 = create_access_token(user1)
        token2 = create_access_token(user2)
        assert token1 != token2

    def test_access_and_refresh_tokens_differ(self):
        user_id = uuid4()
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        assert access != refresh
