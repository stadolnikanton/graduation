import hashlib

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy import select

from app.db import async_session_maker

from core.deps import get_current_user, AuthCookies, get_auth_cookies
from core.secure import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from core.auth_cookies import delete_auth_cookies, set_auth_cookies

from models.token import BlacklistedToken
from models.user import User

from schemas.token import LoginRequest
from schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    user_data: UserCreate,
    response: Response,
    auth_cookies: AuthCookies = Depends(get_auth_cookies)
    ):
    async with async_session_maker() as session:
        email_exists = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if email_exists.scalar_one_or_none():
            raise HTTPException(400, "Email already registered")

        username_exists = await session.execute(
            select(User).where(User.name == user_data.name)
        )
        if username_exists.scalar_one_or_none():
            raise HTTPException(400, "Username already taken")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password=get_password_hash(user_data.password),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return {
            "status": 200,
        }
    


@router.post("/login")
async def login(
    user_data: LoginRequest,
    response: Response,
    auth_cookies: AuthCookies = Depends(get_auth_cookies)
    ):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == user_data.email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return {
            "status": 200,
        }


@router.post("/refresh")
async def refresh(
    request: Request, 
    response: Response,
    auth_cookies: AuthCookies = Depends(get_auth_cookies)
):
    refresh_token = request.cookies.get("refresh_token")

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=422, detail="Not a refresh token")

    user_id = int(payload.get("sub"))

    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return {
            "status": 200,
        }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
):
    async with async_session_maker() as session:
        
        refresh_token = request.cookies.get("refresh_token")

        if refresh_token:
            payload = verify_token(refresh_token)

            if payload:
                jti = payload.get("jti")

                if jti is None:
                    jti = hashlib.sha256(refresh_token.encode()).hexdigest()[:36]
                    
                token_type = payload.get("type", "refresh")
                exp = payload.get("exp")

                blacklisted_token = BlacklistedToken(
                    jti=jti,
                    user_id=current_user.id,
                    token_type=token_type,
                    expires_at=datetime.fromtimestamp(exp),
                    reason="logout",
                )
                session.add(blacklisted_token)
                await session.commit()

        delete_auth_cookies(response)
    
        return {"status": 200, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }
