"""
Unit tests: validaciones de app.schemas.auth
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest


class TestRegisterRequestValidation:
    def test_valid_registration_data(self):
        data = RegisterRequest(
            first_name="Mateo",
            last_name="Rico",
            email="mateo@test.com",
            password="SuperSegura123!",
        )
        assert data.email == "mateo@test.com"

    @pytest.mark.parametrize(
        "password",
        [
            "short1!",  # muy corta
            "sinnumerosnisimbolos",  # sin número ni símbolo
            "SINMINUSCULAS123!",  # sin minúscula
            "sinmayusculas123!",  # sin mayúscula
            "123456789012",  # común / sin letras
        ],
    )
    def test_weak_password_rejected(self, password):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="Mateo",
                last_name="Rico",
                email="mateo@test.com",
                password=password,
            )

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="Mateo",
                last_name="Rico",
                email="not-an-email",
                password="SuperSegura123!",
            )

    def test_blank_first_name_rejected(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="   ",
                last_name="Rico",
                email="mateo@test.com",
                password="SuperSegura123!",
            )
