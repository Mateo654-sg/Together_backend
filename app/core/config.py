"""
Configuración central de la aplicación.

Todas las variables de entorno se cargan y validan aquí mediante
pydantic-settings, siguiendo el principio de nunca hardcodear
datos sensibles (Documento 12 — Seguridad, Documento 16 — Playbook).
"""
from functools import lru_cache

import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación cargada desde variables de entorno.

    Attributes:
        app_env: Entorno de ejecución (development, production, testing).
        app_name: Nombre de la aplicación para el título de Swagger.
        app_version: Versión actual de la API.
        debug: Habilita modo debug (SQLAlchemy echo, etc.).
        database_url: URL de conexión async a PostgreSQL (asyncpg).
        database_url_sync: URL de conexión sync para Alembic (psycopg2).
        redis_url: URL de conexión a Redis para caché.
        jwt_secret: Secreto para firmar tokens JWT (NUNCA exponer).
        jwt_algorithm: Algoritmo de firmado JWT (HS256).
        access_token_expire_minutes: Minutos de vida del access token.
        refresh_token_expire_days: Días de vida del refresh token.
        cors_origins: Orígenes permitidos para CORS.
        openai_api_key: API Key de OpenAI (módulo de IA, futuro).
        aws_access_key_id: ID de acceso AWS (futuro).
        aws_secret_access_key: Secreto de acceso AWS (futuro).
        s3_bucket: Nombre del bucket S3 (futuro).
    """

    # App
    app_env: str = "development"
    app_name: str = "Together API"
    app_version: str = "v1"
    debug: bool = False

    # Database
    database_url: str
    database_url_sync: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8081",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # Google OAuth
    google_web_client_id: str | None = None
    google_web_client_secret: str | None = None
    google_android_client_id: str | None = None
    google_ios_client_id: str | None = None

    # AI (futuro)
    openai_api_key: str | None = None

    # AWS (futuro)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings (Singleton)."""
    return Settings()


settings = get_settings()
