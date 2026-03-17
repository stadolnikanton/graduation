# TODO(REFACTOR-AUTH): Добавить Depends, AsyncSession импорты
# TODO(REFACTOR-AUTH): Добавить зависимости (session, repository, jwt_service, redis_client)
# TODO(REFACTOR-AUTH): Реализовать /register endpoint (полная логика)
# TODO(REFACTOR-AUTH): Реализовать /login endpoint (POST вместо GET)
# TODO(REFACTOR-AUTH): Добавить response_model
# TODO(REFACTOR-AUTH): Обработать ошибки (HTTPException)
# TODO(REFACTOR-AUTH): Вернуть полноценный ответ (user + tokens)
# TODO(REFACTOR-LOGGING): Добавить логирование запросов

from fastapi import APIRouter, requests

from domain.user.services import AuthenticationService
from schemas.requests.authentication import RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login():
    return {200: "success"}


@router.post("/register")
async def register(request: RegisterRequest):
    return await AuthenticationService.register(request)
