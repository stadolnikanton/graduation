from sqlalchemy import select, insert, update, delete

from app.db import async_session_maker
from models.user import User as user_model


class User:
    async def create_user(self, user_data: dict):
        async with async_session_maker() as session:
            user = user_model(**user_data)
            session.add(user)

            await session.commit()
            return user

    def get(self):
        pass
