# TODO(REFACTOR-AUTH): Inject UserRepository через __init__ (вместо session)
# TODO(REFACTOR-AUTH): Inject JWTService через __init__
# TODO(REFACTOR-AUTH): Inject RedisClient через __init__ (опционально)
# TODO(REFACTOR-AUTH): Реализовать register() — полная логика:
#   - Проверка email (через repo)
#   - Проверка username (через repo)
#   - Хеширование пароля
#   - Создание User entity
#   - Сохранение через repo
#   - Создание JWT токенов
# TODO(REFACTOR-AUTH): Реализовать login() — поиск по email/username, проверка пароля, токены
# TODO(REFACTOR-AUTH): Реализовать logout() — blacklist токенов через Redis
# TODO(REFACTOR-AUTH): Реализовать refresh() — обновление токенов
# TODO(REFACTOR-ERRORS): Использовать domain.errors классы
# TODO(REFACTOR-LOGGING): Добавить логирование

from domain.user.entities import User
from infrastructure.repositories.user import UserRepository
from schemas.requests.authentication import LoginRequest, RegisterRequest
from schemas.requests.token import Token


class AuthenticationService:
    def __init__(self, session) -> None:
        self.session = session

    async def register(self, data: RegisterRequest) -> User:
        await UserRepository.create()

    def login(self, data: LoginRequest) -> User:
        pass

    def logout(self):
        pass

    def refresh(self):
        pass
