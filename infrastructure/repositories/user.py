from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user.entities import User
from infrastructure.database.user import UserDB


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        new_user = UserDB(
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            password_hash=user.password_hash,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return self.__convert_to_entity(new_user)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return self.__convert_to_entity(db_user)

        return None

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserDB).where(UserDB.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return self.__convert_to_entity(db_user)

        return None

    async def get_by_id(self, id: int) -> User | None:
        stmt = select(UserDB).where(UserDB.id == id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return self.__convert_to_entity(db_user)

        return None

    def __convert_to_entity(self, user) -> User:
        return User(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
