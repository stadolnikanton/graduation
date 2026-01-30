import secrets
from datetime import datetime, timedelta

from sqlalchemy.future import select

from fastapi import HTTPException

from core.minio_client import download_from_minio
from app.config import settings

from models.file import File as FileModel
from models.link import ShareLink


class Share:
    """Класс контроллер для управления ссылками доступа"""

    def __init__(self, session):
        self.session = session

    async def create_share_link(self, file_id, expires_hours, max_downloads, user):
        stmt = select(FileModel).where(
            FileModel.id == file_id, FileModel.owner == user.id
        )
        result = await self.session.execute(stmt)
        file = result.scalar_one_or_none()

        if not file:
            raise HTTPException(
                status_code=404, detail="File not found or access denied"
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        share_link = ShareLink(
            token=token,
            file_id=file_id,
            expires_at=expires_at,
            max_downloads=max_downloads,
            download_count=0,
            created_at=datetime.now(),
        )

        self.session.add(share_link)
        await self.session.commit()
        await self.session.refresh(share_link)

        return {
            "share_url": f"/share/{token}",
            "expires_at": expires_at.isoformat(),
            "max_downloads": max_downloads,
            "token": token,
        }

    async def get_shared_info(self, token):
        stmt = (
            select(ShareLink, FileModel)
            .join(FileModel, ShareLink.file_id == FileModel.id)
            .where(ShareLink.token == token)
        )
        result = await self.session.execute(stmt)
        result_data = result.first()

        if not result_data:
            raise HTTPException(status_code=404, detail="Link not found")

        share_link, file = result_data

        if share_link.expires_at and share_link.expires_at < datetime.now():
            raise HTTPException(status_code=410, detail="Link has expired")

        if (
            share_link.max_downloads
            and share_link.download_count >= share_link.max_downloads
        ):
            raise HTTPException(status_code=410, detail="Download limit reached")

        return {
            "token": share_link.token,
            "file": {
                "id": file.id,
                "original_filename": file.original_filename,
                "size": file.size,
                "created_at": file.created_at.isoformat() if file.created_at else None,
            },
            "expires_at": (
                share_link.expires_at.isoformat() if share_link.expires_at else None
            ),
            "max_downloads": share_link.max_downloads,
            "downloads_count": share_link.download_count,
            "created_at": (
                share_link.created_at.isoformat() if share_link.created_at else None
            ),
            "is_expired": share_link.expires_at
            and share_link.expires_at < datetime.now(),
            "downloads_left": (
                share_link.max_downloads - share_link.download_count
                if share_link.max_downloads
                else None
            ),
        }

    async def download_shared_file(self, token):
        stmt = select(ShareLink).where(ShareLink.token == token)
        result = await self.session.execute(stmt)
        share_link = result.scalar_one_or_none()

        if not share_link:
            raise HTTPException(status_code=404, detail="Link not found")

        if share_link.expires_at < datetime.now():
            raise HTTPException(status_code=410, detail="Link expired")

        if 1 <= share_link.max_downloads <= share_link.download_count:
            raise HTTPException(status_code=410, detail="Download limit reached")

        file_stmt = select(FileModel).where(FileModel.id == share_link.file_id)
        file_result = await self.session.execute(file_stmt)
        file = file_result.scalar_one_or_none()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        share_link.download_count += 1
        await self.session.commit()

        # Скачиваем файл из MinIO вместо локальной файловой системы
        file_response = download_from_minio(
            file.name, settings.MINIO_BUCKET_NAME, file.original_filename
        )

        if not file_response:
            raise HTTPException(status_code=404, detail="File not found in storage")

        return file_response
