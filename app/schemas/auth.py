"""
Schemas Pydantic del módulo de autenticación.

Todas las validaciones de entrada ocurren aquí (nunca confiar en el
Frontend — Documento 12 y 16).
"""
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{12,}$"
)

# Contraseñas comunes prohibidas explícitamente (Documento 12)
COMMON_PASSWORDS = {
    "123456", "password", "qwerty", "12345678", "123456789", "111111",
}


def validate_strong_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres.")
    if not PASSWORD_REGEX.match(password):
        raise ValueError(
            "La contraseña debe incluir mayúscula, minúscula, número y símbolo."
        )
    if password.lower() in COMMON_PASSWORDS:
        raise ValueError("Esta contraseña es demasiado común.")
    return password


class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_strong_password(v)

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_strong_password(v)


class GoogleLoginRequest(BaseModel):
    id_token: str


class VerifyEmailRequest(BaseModel):
    token: str
