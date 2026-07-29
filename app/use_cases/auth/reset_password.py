import hashlib

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.repositories.user_repository import UserRepository


class ResetPasswordUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.token_repository = PasswordResetTokenRepository(session)

    async def execute(self, token: str, new_password: str) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        reset_token = await self.token_repository.get_valid_by_token_hash(token_hash)

        if reset_token is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado.",
            )

        user = await self.user_repository.get_by_id(reset_token.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado.",
            )

        user.password_hash = hash_password(new_password)
        await self.token_repository.mark_used(reset_token)
        await self.session.commit()
