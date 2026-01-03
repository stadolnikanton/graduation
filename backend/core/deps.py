from fastapi import HTTPException, status, Request, Response
from typing import Optional, Dict, Any

from sqlalchemy import select

from app.db import async_session_maker

from models.user import User

from core.secure import verify_token
from core.auth_cookies import set_auth_cookies, delete_auth_cookies, set_auth_cookies_with_user_data


class AuthCookies:
    """Класс для удобного управления auth cookies через Depends"""
    
    def __init__(self, response: Response):
        self.response = response
    
    def set(
        self, 
        access_token: str, 
        refresh_token: str,
        secure: Optional[bool] = None,
        path: str = "/"
    ) -> None:
        set_auth_cookies(self.response, access_token, refresh_token, secure, path)
    
    def delete(self, path: str = "/") -> None:
        delete_auth_cookies(self.response, path)
    
    def set_with_user_data(
        self,
        access_token: str,
        refresh_token: str,
        user_data: Dict[str, Any],
        secure: Optional[bool] = None,
        path: str = "/"
    ) -> None:
        set_auth_cookies_with_user_data(
            self.response, access_token, refresh_token, user_data, secure, path
        )
    
    def set_custom(
        self,
        key: str,
        value: str,
        max_age: int = None,
        httponly: bool = True,
        secure: bool = None,
        samesite: str = "strict",
        path: str = "/"
    ) -> None:
        if secure is None:
            secure = False
            
        self.response.set_cookie(
            key=key,
            value=value,
            httponly=httponly,
            max_age=max_age,
            secure=secure,
            samesite=samesite,
            path=path,
        )


def get_auth_cookies(response: Response) -> AuthCookies:
    return AuthCookies(response)



async def get_current_user(request: Request):
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Access token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_token(access_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise HTTPException(status_code=422, detail="Not an access token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    async with async_session_maker() as session:
        stmt = select(User).where(User.id == int(user_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    return user

