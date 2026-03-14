from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.users.models import User
from app.core.security import verify_password, create_access_token
from app.auth.dto import LoginRequest, Token

class AuthService:
    @staticmethod
    async def authenticate(db: AsyncSession, login_data: LoginRequest) -> Token:
        # 1. Find user by email
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalars().first()

        # 2. Check if user exists and password matches
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        # 3. Generate JWT
        access_token = create_access_token(subject=user.id, tenant_id=user.tenant_id)
        
        return Token(access_token=access_token, token_type="bearer")
