"""
Excepciones de dominio.

Estas excepciones nunca exponen detalles internos (stacktraces,
excepciones de SQLAlchemy, etc.) al usuario final. El manejador
global en app/main.py las traduce al formato oficial de respuesta
de error definido en el Documento 08 — Backend API.
"""


class AppException(Exception):
    """Excepción base de la aplicación."""

    status_code: int = 400
    message: str = "Ocurrió un error inesperado."

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    status_code = 404
    message = "Recurso no encontrado."


class UnauthorizedException(AppException):
    status_code = 401
    message = "No autorizado."


class ForbiddenException(AppException):
    status_code = 403
    message = "No tienes permisos para realizar esta acción."


class ConflictException(AppException):
    status_code = 409
    message = "El recurso ya existe."


class ValidationException(AppException):
    status_code = 422
    message = "Datos inválidos."


class TooManyRequestsException(AppException):
    status_code = 429
    message = "Demasiados intentos. Intenta más tarde."


# --- Excepciones específicas del dominio Auth/Users ---


class InvalidCredentialsException(UnauthorizedException):
    message = "Correo o contraseña incorrectos."


class EmailAlreadyExistsException(ConflictException):
    message = "Este correo ya está registrado."


class InvalidTokenException(UnauthorizedException):
    message = "Token inválido o expirado."


class AccountLockedException(TooManyRequestsException):
    message = "Cuenta bloqueada temporalmente por múltiples intentos fallidos."
