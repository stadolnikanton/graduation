from fastapi import Depends, HTTPException, status, Request

from sqlalchemy import select

from app.db import async_session_maker

from models.user import User

from core.secure import verify_token


def get_current_user_id(requset: Request):
    access_token = requset.cookies.get("access_token")

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
    
    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user id in token")


async def get_current_user(request: Request):
    user_id = get_current_user_id(request)

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