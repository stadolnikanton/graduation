from typing import List
from xmlrpc.client import FastParser

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.file.entities import File
from infrastructure.database.file import FileDB, FileSharesDB


class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, file: File) -> File:
        new_file = FileDB(
            hash_name=file.hash_name,
            original_filename=file.original_filename,
            type=file.type,
            owner=file.owner,
            path=file.path,
            size=file.size,
        )
        self.session.add(new_file)

        await self.session.commit()
        await self.session.refresh(new_file)

        return FileRepository.__convert_to_entity(new_file)

    async def get_by_filename(self, filename: str) -> File | None:
        stmt = select(FileDB).where(FileDB.original_filename == filename)
        result = await self.session.execute(stmt)
        file = result.scalar_one_or_none()

        if file:
            return FileRepository.__convert_to_entity(file)
        return None

    async def get_by_id(self, id: int) -> File | None:
        stmt = select(FileDB).where(FileDB.id == id)
        result = await self.session.execute(stmt)
        file = result.scalar_one_or_none()

        if file:
            return FileRepository.__convert_to_entity(file)
        else:
            return None

    async def file_by_filename_exists_for_user(
        self, filename: str, user_id: int
    ) -> bool:
        stmt = (
            select(FileDB)
            .where(FileDB.original_filename == filename)
            .where(FileDB.owner == user_id)
        )
        result = await self.session.execute(stmt)
        file = result.scalar_one_or_none()

        if file:
            return True
        return False

    async def file_by_id_exists_for_user(self, file_id: int, user_id: int):
        stmt = select(FileDB).where(FileDB.id == file_id).where(FileDB.owner == user_id)
        result = await self.session.execute(stmt)
        file = result.scalar_one_or_none()

        if file:
            return file
        return False

    async def file_delete(self, file_id: int, user_id: int) -> File | bool:
        file = await self.file_by_id_exists_for_user(file_id, user_id)

        if file:
            await self.session.delete(file)
            await self.session.commit()

            return FileRepository.__convert_to_entity(file)
        return False

    async def get_all_file(self, user_id) -> List[File]:
        files = []
        stmt = select(FileDB).where(FileDB.owner == user_id).order_by(FileDB.created_at)
        result = await self.session.execute(stmt)

        result = result.scalars().all()
        for file in result:
            files.append(FileRepository.__convert_to_entity(file))

        return files

    @staticmethod
    def __convert_to_entity(file) -> File:
        return File(
            id=file.id,
            hash_name=file.hash_name,
            original_filename=file.original_filename,
            type=file.type,
            owner=file.owner,
            path=file.path,
            size=file.size,
            created_at=file.created_at,
        )
