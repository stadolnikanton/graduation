import hashlib
from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from core.auth_cookies import delete_auth_cookies, set_auth_cookies
from core.secure import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from core.deps import get_db
from models.token import BlacklistedToken
from models.user import User


class Authentication:
    """Класс контроллер для аутентификации"""

    def __init__(self, session: AsyncSession = Depends(get_db())):
        self.session = session

    async def login(self, user_data, response):
        result = await self.session.execute(
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

        return

    async def register(self, user_data, response):
        email_exists = await self.session.execute(
            select(User).where(User.email == user_data.email)
        )
        if email_exists.scalar_one_or_none():
            raise HTTPException(400, "Email already registered")

        username_exists = await self.session.execute(
            select(User).where(User.name == user_data.name)
        )
        if username_exists.scalar_one_or_none():
            raise HTTPException(400, "Username already taken")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password=get_password_hash(user_data.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return

    async def refresh(self, request, response):
        refresh_token = request.cookies.get("refresh_token")

        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=422, detail="Not a refresh token")

        user_id = int(payload.get("sub"))

        result = await self.session.execute(select(User).where(User.id == user_id))

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        set_auth_cookies(response, access_token, refresh_token)

        return

    async def logout(self, request, response, current_user):
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
                self.session.add(blacklisted_token)
                await self.session.commit()

        delete_auth_cookies(response)

        return

    async def get_current_user(self, current_user):
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "created_at": (
                current_user.created_at.isoformat() if current_user.created_at else None
            ),
        }
