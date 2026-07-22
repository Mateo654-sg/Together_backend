"""
Generación de códigos de invitación (FR-011).

Se excluyen caracteres ambiguos (0/O, 1/I/L) para que el código sea
fácil de leer y compartir manualmente entre la pareja.
"""
import secrets

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 8


def generate_invitation_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
