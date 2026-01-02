import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy import select

from app.db import async_session_maker

from core.deps import get_current_user, oauth2_scheme
from core.secure import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from models.token import BlacklistedToken
from models.user import User
from schemas.token import LoginRequest, RefreshTokenRequest, Token
from schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, response: Response):
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

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=30*60,
            secure=False,
            samesite="strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60,
            secure=False,  # True в production с HTTPS
            samesite="strict"
        )

        return {
            "status": 200,
        }


@router.post("/login", response_model=Token)
async def login(user_data: LoginRequest, response: Response):
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

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=30*60,
            secure=False,
            samesite="strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60,
            secure=False,  # True в production с HTTPS
            samesite="strict"
        )

        return {
            "status": 200,
        }


@router.post("/refresh", response_model=Token)
async def refresh(request: Request, response: Response):
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

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=30*60,
            secure=False,
            samesite="strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60,
            secure=False,  # True в production с HTTPS
            samesite="strict"
        )

        return {
            "status": 200,
        }


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    async with async_session_maker() as session:
        
        token = response.cookies.get("refresh_token")
        
        payload = verify_token(token)

        if not payload:
            return {
                "status": "success",
                "message": "Token invalid or expired, considered logged out",
            }

        jti = payload.get("jti")
        exp = payload.get("exp")

        existing = await session.execute(
            select(BlacklistedToken).where(BlacklistedToken.jti == jti)
        )
        if existing.scalar_one_or_none():
            return {"status": "success", "message": "Already logged out"}

        blacklisted_access = BlacklistedToken(
            jti=jti,
            user_id=current_user.id,
            token_type="access",
            expires_at=datetime.fromtimestamp(exp),
            reason="logout",
        )
        session.add(blacklisted_access)
        await session.commit()

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
    
        return {"status": 200, "message": "Logged out successfully"}
