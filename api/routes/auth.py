from unittest import result
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from schemas.user import UserCreate, UserResponse

from models.user import User
from app.db import async_session_maker
from schemas.token import Token, LoginRequest, RefreshTokenRequest
from core.secure import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
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

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


@router.post("/login", response_model=Token)
async def login(user_data: LoginRequest):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == user_data.email))
        
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")
            
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }