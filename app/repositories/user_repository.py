"""
Repository de User.

Encapsula todas las consultas relacionadas al modelo User.
Nunca se accede a la base de datos directamente desde services o use cases.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(
            User.email == email.lower(), User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        stmt = select(User).where(
            User.google_id == google_id, User.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def increment_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts += 1
        await self.session.flush()

    async def reset_failed_attempts(self, user: User) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()
