import secrets

from datetime import datetime, timedelta

from domain.file.services import FileUploadService
from domain.user.entities import User
from domain.share.entities import ShareLink
from domain.errors import FileNotFoundError, TokenNotFoundError, TokenTimeOutError, TokenMaxDownloadError

from infrastructure.repositories.file import FileRepository
from infrastructure.repositories.share import ShareRepository


class ShareServices:
    def __init__(self, file_repo: FileRepository, share_repo: ShareRepository, file_services: FileUploadService) -> None:
        self.file_repo = file_repo
        self.share_repo = share_repo
        self.file_services = file_services


    async def create_share_link(self, file_id: int, user: User, expires_hours: int | None = None, max_downloads: int | None = None):
        try:
            file = await self.file_repo.file_by_id_exists_for_user(file_id, user.id)
            if not file:
                raise FileNotFoundError()
            
            token = secrets.token_urlsafe(32)

            if expires_hours is not None:
                expires_at = datetime.now() + timedelta(hours=expires_hours)
            else:
                expires_at = expires_hours 
            share = ShareLink(
                    token=token,
                    file_id=file.id,
                    expires_at=expires_at,
                    max_downloads=max_downloads,
                    download_count=0,
                    created_at=datetime.now(),
                    )
            share_link = await self.share_repo.create(share)

            return {
                    "share_url": f"/v1/share/{share_link.token}",
                    "expires_at": share_link.expires_at.isoformat() if share_link.expires_at else None,
                    "max_downloads": share_link.max_downloads,
                    "token": share_link.token
                    }

        except FileNotFoundError as e:
            return {
                    "status": e.status_code,
                    "message": e.default_message, 
                    }
    async def delete_shared_link(self, token):
        try:
            share = await self.share_repo.delete_file_by_token(token)
            if share is None:
                raise TokenNotFoundError() 
            return {
                    "status": 204,
                    "message": "Link was been deleted",
                    "token": f"{share.token}"
                    } 
        except TokenNotFoundError as e:
            return {
                    "status": e.status_code,
                    "message": e.default_message
                    }

    async def download_shared_file(self, token):
        try:
            share_link = await self.share_repo.get_file_by_token(token)
            if share_link is None:
                raise TokenNotFoundError()

            if share_link.expires_at is not None and share_link.expires_at <= datetime.now():
                raise TokenTimeOutError()

            if share_link.max_downloads is not None and share_link.download_count >= share_link.max_downloads:
                raise TokenMaxDownloadError()

            await self.share_repo.increment_download_count(token)

            return await self.file_services.file_download_by_id(share_link.file_id)

        except (FileNotFoundError, TokenNotFoundError, TokenTimeOutError, TokenMaxDownloadError) as e:
            return {
                    "status": e.status_code,
                    "message": e.default_message,
                    }

    async def get_shared_info(self, token):
        try:
            file_info = await self.share_repo.get_file_by_token(token)
            if file_info is None:
                raise TokenNotFoundError()

            if file_info.expires_at is not None and file_info.expires_at <= datetime.now():
                raise TokenTimeOutError()

            if file_info.max_downloads is not None and file_info.download_count >= file_info.max_downloads:
                raise TokenMaxDownloadError()

            return {
                    "id": file_info.id,
                    "token": file_info.token,
                    "file_id": file_info.file_id,
                    "expires_at": file_info.expires_at.isoformat() if file_info.expires_at else None,
                    "max_downloads": file_info.max_downloads,
                    "download_count": file_info.download_count,
                    "created_at": file_info.created_at.isoformat() if file_info.created_at else None,
                    }
        except (TokenNotFoundError, TokenTimeOutError, TokenMaxDownloadError) as e:
            return {
                    "status": e.status_code,
                    "message": e.default_message,
                    }
