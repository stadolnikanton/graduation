from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_current_user, get_db
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

    return {"status": 200}


@router.post("/login")
async def login(
    user_data: LoginRequest, response: Response, session: AsyncSession = Depends(get_db)
):
    auth = Authentication(session)
    await auth.login(user_data, response)

    return {"status": 200}


@router.post("/refresh")
async def refresh(
    request: Request, response: Response, session: AsyncSession = Depends(get_db)
):
    auth = Authentication(session)
    await auth.refresh(request, response)
    return {"status": 200}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    auth = Authentication(session)
    await auth.logout(request, response, current_user)

    return {
        "status": 200,
        "message": "Logged out successfully",
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    auth = Authentication(session)

    return await auth.get_current_user(current_user)
