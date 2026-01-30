import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.db import async_session_maker
from core.auth_cookies import delete_auth_cookies, set_auth_cookies
from core.deps import get_current_user, get_db
from core.secure import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from models.token import BlacklistedToken
from models.user import User
from schemas.token import LoginRequest
from schemas.user import UserCreate


from api.services.authentication import Authentication

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    user_data: UserCreate,
    response: Response,
    session: AsyncSession = Depends(get_db),
):
    auth = Authentication(session)
    await auth.register(user_data, response)

    return {"status": "ok"}


@router.post("/login")
async def login(
    user_data: LoginRequest, response: Response, session: AsyncSession = Depends(get_db)
):
    auth = Authentication(session)
    await auth.login(user_data, response)

    return {"status": "200"}


@router.post("/refresh")
async def refresh(
    request: Request, response: Response, session: AsyncSession = Depends(get_db)
):
    auth = Authentication(session)
    await auth.refresh(request, response)
    return {"status": "200"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    auth = Authentication(session)
    await auth.logout(request, response, current_user)

    return {"status": "200"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    auth = Authentication(session)

    response = await auth.get_current_user(current_user)
    return response
