"""
Configuración central de la aplicación.

Todas las variables de entorno se cargan y validan aquí mediante
pydantic-settings, siguiendo el principio de nunca hardcodear
datos sensibles (Documento 12 — Seguridad, Documento 16 — Playbook).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_name: str = "Together API"
    app_version: str = "v1"
    debug: bool = True

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
    cors_origins: list[str] = ["http://localhost:3000"]

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
