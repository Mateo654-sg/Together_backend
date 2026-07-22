"""
Fixtures compartidos de pytest.

Usa una base de datos PostgreSQL de pruebas separada (together_test_db)
(Documento 13 — Testing Strategy: nunca utilizar datos reales, aislamiento
total entre tests).

Nota técnica: el engine async se crea con scope de función (no de módulo)
porque las conexiones de asyncpg quedan atadas al event loop en el que
fueron creadas, y pytest-asyncio crea un event loop nuevo por test.
"""
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://together:together@localhost:5432/together_test_db"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
