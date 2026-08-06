from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_device_info
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.use_cases.auth.forgot_password import ForgotPasswordUseCase
from app.use_cases.auth.google_login import GoogleLoginUseCase
from app.use_cases.auth.login_user import LoginUserUseCase
from app.use_cases.auth.logout_user import LogoutUserUseCase
from app.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.use_cases.auth.register_user import RegisterUserUseCase
from app.use_cases.auth.reset_password import ResetPasswordUseCase
from app.use_cases.auth.verify_email import VerifyEmailUseCase

router = APIRouter(prefix="/auth", tags=["Auth"])

REFRESH_COOKIE_KEY = "refresh_token"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_KEY,
        path="/api/v1",
        secure=settings.is_production,
        samesite="none",
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
    device: str | None = Depends(get_device_info),
):
    """FR-001: Crear una cuenta mediante correo electrónico y emitir tokens."""
    use_case = RegisterUserUseCase(db)
    result = await use_case.execute(data, ip=ip, device=device)
    response.status_code = status.HTTP_201_CREATED
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1",
    )
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        verification_token=result.verification_token,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
    device: str | None = Depends(get_device_info),
):
    """FR-002: Iniciar sesión."""
    use_case = LoginUserUseCase(db)
    result = await use_case.execute(data, ip=ip, device=device)
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1",
    )
    return TokenResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post("/google", response_model=TokenResponse)
@limiter.limit("5/minute")
async def google_login(
    request: Request,
    data: GoogleLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    ip: str | None = Depends(get_client_ip),
    device: str | None = Depends(get_device_info),
):
    """Login/registro con Google OAuth."""
    use_case = GoogleLoginUseCase(db)
    result = await use_case.execute(data, ip=ip, device=device)
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1",
    )
    return TokenResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verificar correo electrónico tras el registro (flujo Doc 05)."""
    use_case = VerifyEmailUseCase(db)
    await use_case.execute(data.token)
    return None


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Renueva el Access Token mediante rotación de Refresh Token.

    El refresh token explícito del body tiene prioridad; en su defecto se lee
    de la cookie HttpOnly.
    """
    refresh_token = data.refresh_token if data is not None else None
    if not refresh_token:
        refresh_token = request.cookies.get(REFRESH_COOKIE_KEY)
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token no encontrado en la cookie.")

    use_case = RefreshTokenUseCase(db)
    result = await use_case.execute_str(refresh_token)
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none",
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1",
    )
    return TokenResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    data: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """FR-005: Cerrar sesión."""
    refresh_token = request.cookies.get(REFRESH_COOKIE_KEY)
    if not refresh_token and data is not None:
        refresh_token = data.refresh_token
    if not refresh_token:
        return None

    use_case = LogoutUserUseCase(db)
    await use_case.execute_str(refresh_token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=REFRESH_COOKIE_KEY,
        path="/api/v1",
        secure=settings.is_production,
        samesite="none",
    )
    return response


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """FR-003: Recuperar contraseña (envío de correo con token).

    Se retorna 204 siempre, exista o no el correo, para evitar
    enumeración de usuarios (buena práctica de seguridad).
    """
    use_case = ForgotPasswordUseCase(db)
    await use_case.execute(data.email)
    return None


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """FR-003: Restablecer contraseña mediante token."""
    use_case = ResetPasswordUseCase(db)
    await use_case.execute(data.token, data.new_password)
    return None
