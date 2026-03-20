import os
import uuid
import anyio

from app.config import settings
from core.minio_client import (
    delete_from_minio,
    download_from_minio,
    ensure_bucket_exists,
    upload_file,
)
from fastapi import HTTPException
from models.file import File as FileModel
from models.file import FileShares
from models.link import ShareLink
from models.user import User
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError


class Upload:
    """Класс контроллер для управления файлами"""

    def __init__(self, session):
        self.session = session
        self.MAX_FILE_SIZE = 100 * 1024 * 1024
        self.MAX_TOTAL_SIZE = 500 * 1024 * 1024
        self.MAX_FILE_SIZE = 100 * 1024 * 1024

    async def get_files_user(self, user):
        result = await self.session.execute(
            select(FileModel)
            .where(FileModel.owner == user.id)
            .order_by(FileModel.created_at.desc())
        )
        owned_files_result = result.scalars().all()

        ownded_files = []
        for file in owned_files_result:
            ownded_files.append(
                {
                    "id": file.id,
                    "name": file.name,
                    "original_filename": file.original_filename,
                    "type": file.type,
                    "size": file.size,
                    "created_at": (
                        file.created_at.isoformat() if file.created_at else None
                    ),
                    "download_url": f"/files/{file.id}/download",
                    "is_owner": True,
                    "shared_file": False,
                }
            )

        result = await self.session.execute(
            select(FileModel)
            .join(FileShares, FileModel.id == FileShares.file_id)
            .where(FileShares.user_id == user.id)
            .order_by(FileShares.shared_at.desc())
        )
        shared_files_result = result.scalars().all()

        shared_files = []
        for file in shared_files_result:
            shared_files.append(
                {
                    "id": file.id,
                    "name": file.name,
                    "original_filename": file.original_filename,
                    "type": file.type,
                    "size": file.size,
                    "created_at": (
                        file.created_at.isoformat() if file.created_at else None
                    ),
                    "download_url": f"/files/{file.id}/download",
                    "is_owner": False,
                    "shared_file": True,
                }
            )

        return {
            "files": {"owned": ownded_files, "shared": shared_files},
            "counts": {
                "owned": len(ownded_files),
                "shared": len(shared_files),
                "total": len(ownded_files) + len(shared_files),
            },
        }

    async def grant_file_access(self, data, file_id, user):
        result = await self.session.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise HTTPException(404, "Файл не найден")

        if db_file.owner != user.id:
            raise HTTPException(403, "Нет доступа к файлу")

        if data.user_id == user.id:
            raise HTTPException(400, "Нельзя поделиться с самим собой")

        result = await self.session.execute(select(User).where(User.id == data.user_id))
        recipient = result.scalar_one_or_none()

        if not recipient:
            raise HTTPException(404, "Пользователь-получатель не найден")

        result = await self.session.execute(
            select(FileShares).where(
                FileShares.file_id == file_id,
                FileShares.user_id == data.user_id,
            )
        )
        existing_share = result.scalar_one_or_none()

        if existing_share:
            raise HTTPException(409, "Доступ уже предоставлен этому пользователю")

        try:
            new_share = FileShares(
                file_id=file_id,
                user_id=data.user_id,
                owner_id=user.id,
                access_level=data.access_level,
            )

            self.session.add(new_share)
            await self.session.commit()
            await self.session.refresh(new_share)

            return {
                "message": "Доступ успешно предоставлен",
                "share_id": new_share.id,
                "file_id": file_id,
                "recipient_id": data.user_id,
                "access_level": data.access_level,
            }

        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(500, "Ошибка при предоставлении доступа")

    async def get_shared_users(self, file_id):
        result = await self.session.execute(
            select(FileShares.user_id, FileShares.access_level).where(
                FileShares.file_id == file_id
            )
        )
        shared_records = result.all()

        if not shared_records:
            return []

        user_ids = [record.user_id for record in shared_records]

        users_result = await self.session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = users_result.scalars().all()

        users_dict = {user.id: user for user in users}

        response = []
        for record in shared_records:
            user = users_dict.get(record.user_id)
            if user:
                response.append(
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "access_level": record.access_level,
                    }
                )

        return response

    async def remove_file_share(self, file_id, user_id, user):
        result = await self.session.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise HTTPException(404, "Файл не найден")

        if db_file.owner != user.id:
            raise HTTPException(403, "Вы не владелец этого файла")

        if user_id == user.id:
            raise HTTPException(400, "Нельзя удалить доступ самому себе")

        result = await self.session.execute(
            select(FileShares).where(
                FileShares.file_id == file_id, FileShares.user_id == user_id
            )
        )
        file_share = result.scalar_one_or_none()

        if not file_share:
            raise HTTPException(404, "Доступ не найден")

        await self.session.delete(file_share)
        await self.session.commit()

        return {
            "message": "Доступ успешно удален",
            "file_id": file_id,
            "removed_user_id": user_id,
        }

    async def download_file(self, file_id, user):
        result = await self.session.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        if db_file.owner != user.id:
            result = await self.session.execute(
                select(FileShares).where(
                    FileShares.file_id == file_id,
                    FileShares.user_id == user.id,
                )
            )
            access_file = result.scalar_one_or_none()

            if not access_file:
                raise HTTPException(status_code=403, detail="Нет доступа к файлу")

        file_response = download_from_minio(
            db_file.name, settings.MINIO_BUCKET_NAME, db_file.original_filename
        )

        if not file_response:
            raise HTTPException(
                status_code=404,
                detail=f"Файл '{db_file.original_filename}' отсутствует в хранилище",
            )

        return file_response
