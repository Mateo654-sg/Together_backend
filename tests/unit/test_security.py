"""
Unit tests: app.core.security

Nunca acceden a la base de datos (Documento 13 — Testing Strategy).
"""
import time

import pytest

from app.core.exceptions import InvalidTokenException
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_different_string(self):
        password = "SuperSegura123!"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$argon2id$")

    def test_verify_password_correct(self):
        password = "SuperSegura123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("SuperSegura123!")
        assert verify_password("OtraClave456!", hashed) is False

    def test_same_password_generates_different_hashes(self):
        """Argon2 usa salt aleatorio: dos hashes del mismo password difieren."""
        password = "SuperSegura123!"
        assert hash_password(password) != hash_password(password)


class TestJWT:
    def test_create_and_decode_access_token(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token, jti = create_access_token(user_id)
        payload = decode_token(token, expected_type=TokenType.ACCESS)

        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert payload["jti"] == jti

    def test_create_and_decode_refresh_token(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token, jti = create_refresh_token(user_id)
        payload = decode_token(token, expected_type=TokenType.REFRESH)

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_decode_with_wrong_type_raises(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token, _ = create_access_token(user_id)

        with pytest.raises(InvalidTokenException):
            decode_token(token, expected_type=TokenType.REFRESH)

    def test_decode_invalid_token_raises(self):
        with pytest.raises(InvalidTokenException):
            decode_token("this.is.not.a.valid.token", expected_type=TokenType.ACCESS)

    def test_access_and_refresh_have_different_jti(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        _, access_jti = create_access_token(user_id)
        _, refresh_jti = create_refresh_token(user_id)
        assert access_jti != refresh_jti
