"""
Together API — Entry point.

Inicializa la aplicación FastAPI con:
- CORS restringido a los orígenes configurados en CORS_ORIGINS.
- Rate limiting global vía SlowAPI.
- Cabeceras de seguridad HTTP (HSTS, CSP, etc.) vía middleware propio.
- Documentación interactiva deshabilitada en producción para reducir
  la superficie de ataque (sólo accesible en desarrollo/staging).
- Manejadores de error unificados con el formato:
    { "success": false, "message": "...", "errors": [] }
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.rate_limit import limiter
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)

# En producción ocultamos los endpoints de documentación para reducir la
# superficie de ataque. En desarrollo permanecen activos para facilitar el
# trabajo del equipo.
_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"
_openapi_url = None if settings.is_production else "/openapi.json"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Métodos HTTP explícitos: limitamos a los que realmente usa la API para
# evitar que CORS autorice verbos no controlados (p. ej. TRACE).
_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
_ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "X-Requested-With",
    "X-Request-ID",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=_ALLOWED_METHODS,
    allow_headers=_ALLOWED_HEADERS,
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "errors": []},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Datos inválidos.",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.message, "errors": []},
        )
    logger.exception(
        "Unhandled error on %s %s", request.method, request.url.path, exc_info=exc
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Parece que ocurrió un problema. Intentemos nuevamente.",
            "errors": [],
        },
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


app.include_router(api_router)
