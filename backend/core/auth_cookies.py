import logging

from fastapi import Response
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)

ACCESS_TOKEN_MAX_AGE = 30 * 60 
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  
HTTPONLY = True
SECURE = False # В продакшене изменить на True, False только для локальной разработки
SAME_SITE = "lax"
COOKIE_PATH = "/"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    secure: Optional[bool] = None,
    path: str = COOKIE_PATH
) -> None:
    use_secure = secure if secure is not None else SECURE
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=HTTPONLY,
        max_age=ACCESS_TOKEN_MAX_AGE,
        secure=use_secure,
        samesite=SAME_SITE,
        path=path,
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=HTTPONLY,
        max_age=REFRESH_TOKEN_MAX_AGE,
        secure=use_secure,
        samesite=SAME_SITE,
        path=path,
    )
    
    logger.debug(f"Auth cookies set for path: {path}")


def delete_auth_cookies(response: Response, path: str = COOKIE_PATH) -> None:
    response.delete_cookie(key="access_token", path=path)
    response.delete_cookie(key="refresh_token", path=path)
    
    logger.debug(f"Auth cookies deleted for path: {path}")


def set_auth_cookies_with_user_data(
    response: Response,
    access_token: str,
    refresh_token: str,
    user_data: Dict[str, Any],
    secure: Optional[bool] = None,
    path: str = COOKIE_PATH
    ) -> None:
    set_auth_cookies(response, access_token, refresh_token, secure, path)
    
    if "username" in user_data:
        response.set_cookie(
            key="user_name",
            value=user_data["username"],
            httponly=False,
            max_age=REFRESH_TOKEN_MAX_AGE,
            secure=secure if secure is not None else SECURE,
            samesite=SAME_SITE,
            path=path,
        )
    
    if "user_id" in user_data:
        response.set_cookie(
            key="user_id",
            value=str(user_data["user_id"]),
            httponly=False,
            max_age=REFRESH_TOKEN_MAX_AGE,
            secure=secure if secure is not None else SECURE,
            samesite=SAME_SITE,
            path=path,
        )
    
    logger.debug(f"Auth cookies with user data set for user: {user_data.get('user_id')}")
