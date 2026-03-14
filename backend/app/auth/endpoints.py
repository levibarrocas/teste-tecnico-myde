from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dto import LoginRequest, Token, UserRead
from app.auth.service import AuthService
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.core.limiter import limiter

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    return await AuthService.authenticate(db, login_data)

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return current_user
