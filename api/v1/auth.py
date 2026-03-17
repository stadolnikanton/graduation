# TODO(REFACTOR-AUTH): Добавить Depends, AsyncSession импорты
# TODO(REFACTOR-AUTH): Добавить зависимости (session, repository, jwt_service, redis_client)
# TODO(REFACTOR-AUTH): Реализовать /register endpoint (полная логика)
# TODO(REFACTOR-AUTH): Реализовать /login endpoint (POST вместо GET)
# TODO(REFACTOR-AUTH): Добавить response_model
# TODO(REFACTOR-AUTH): Обработать ошибки (HTTPException)
# TODO(REFACTOR-AUTH): Вернуть полноценный ответ (user + tokens)
# TODO(REFACTOR-LOGGING): Добавить логирование запросов

from fastapi import APIRouter, Response
from fastapi.params import Depends

from api.deps import get_auth_service
from domain.user.services import AuthenticationService
from infrastructure.security.cookies import set_auth_cookies
from schemas.requests.authentication import LoginRequest, RegisterRequest

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
