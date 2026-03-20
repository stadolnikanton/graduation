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


