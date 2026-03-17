from fastapi import APIRouter, Request, Response
from fastapi.params import Depends

from api.deps import delete_auth_cookies, get_auth_service, get_current_user
from domain.user.services import AuthenticationService
from infrastructure.security.cookies import set_auth_cookies
from schemas.requests.authentication import LoginRequest, RegisterRequest
from schemas.responses.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    data: LoginRequest,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    result = await auth_service.login(data)
    set_auth_cookies(response, result["access_token"], result["refresh_token"])


@router.post("/register")
async def register(
    data: RegisterRequest,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    result = await auth_service.register(data)
    set_auth_cookies(response, result["access_token"], result["refresh_token"])


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    await auth_service.logout(request)
    delete_auth_cookies(response)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    delete_auth_cookies(response)
    result = await auth_service.refresh(request)
    set_auth_cookies(response, result["access_token"], result["refresh_token"])


@router.get("/me", response_model=UserResponse)
async def me(
    current_user=Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    return await auth_service.me(current_user.id)
