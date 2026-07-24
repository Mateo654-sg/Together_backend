"""
Configuración de conexión a PostgreSQL mediante SQLAlchemy 2 (async).

Nunca se accede a la base de datos directamente desde routers o
la UI: siempre a través de Repositories (Documento 06 — Arquitectura).
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency de FastAPI que provee una sesión de base de datos por request.

    Se encarga de:
    - Crear una nueva sesión por cada request HTTP.
    - Hacer rollback automático si ocurre una excepción.
    - Cerrar la sesión al finalizar el request.

    Yields:
        AsyncSession: Sesión async de SQLAlchemy para usar en repositories.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
