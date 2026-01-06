import secrets

from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.future import select

from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import FileResponse

from app.db import async_session_maker
from core.deps import get_current_user

from models.file import File as FileModel
from models.link import ShareLink
from models.user import User

router = APIRouter(prefix="/share", tags=["share"])


@router.post("/{file_id}")
async def create_share_link(
    file_id: int,
    expires_hours: int = Form(24),
    max_downloads: int = Form(1),
    user: User = Depends(get_current_user)
):
    
    async with async_session_maker() as session:
        stmt = select(FileModel).where(
            FileModel.id == file_id, 
            FileModel.owner == user.id
        )
        result = await session.execute(stmt)
        file = result.scalar_one_or_none()

        if not file:
            raise HTTPException(
                status_code=404, 
                detail="File not found or access denied"
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        share_link = ShareLink(
            token=token,
            file_id=file_id,
            expires_at=expires_at,
            max_downloads=max_downloads,
            download_count=0,
            created_at=datetime.now()
        )

        session.add(share_link)
        await session.commit()
        await session.refresh(share_link)
        
        return {
            "share_url": f"/share/{token}",
            "expires_at": expires_at.isoformat(),
            "max_downloads": max_downloads,
            "token": token
        }


@router.get("/{token}/info")
async def get_shared_info(token: str):
    async with async_session_maker() as session:
        stmt = select(ShareLink, FileModel).join(FileModel, ShareLink.file_id == FileModel.id).where(ShareLink.token == token)
        result = await session.execute(stmt)
        result_data = result.first()
        
        if not result_data:
            raise HTTPException(status_code=404, detail="Link not found")
        
        share_link, file = result_data
        
        if share_link.expires_at and share_link.expires_at < datetime.now():
            raise HTTPException(status_code=410, detail="Link has expired")
        
        if share_link.max_downloads and share_link.download_count >= share_link.max_downloads:
            raise HTTPException(status_code=410, detail="Download limit reached")
        
        return {
            "token": share_link.token,
            "file": {
                "id": file.id,
                "original_filename": file.original_filename,
                "size": file.size,
                "created_at": file.created_at.isoformat() if file.created_at else None
            },
            "expires_at": share_link.expires_at.isoformat() if share_link.expires_at else None,
            "max_downloads": share_link.max_downloads,
            "downloads_count": share_link.download_count,
            "created_at": share_link.created_at.isoformat() if share_link.created_at else None,
            "is_expired": share_link.expires_at and share_link.expires_at < datetime.now(),
            "downloads_left": (
                share_link.max_downloads - share_link.download_count 
                if share_link.max_downloads else None
            )
        }


@router.get("/{token}")
async def download_shared_file(token: str):
    async with async_session_maker() as session:
        stmt = select(ShareLink).where(ShareLink.token == token)
        result = await session.execute(stmt)
        share_link = result.scalar_one_or_none()

        if not share_link:
            raise HTTPException(status_code=404, detail="Link not found")

        if share_link.expires_at < datetime.now():
            raise HTTPException(status_code=410, detail="Link expired")

        if share_link.max_downloads >= 1 and share_link.download_count >= share_link.max_downloads:
            raise HTTPException(status_code=410, detail="Download limit reached")

        file_stmt = select(FileModel).where(FileModel.id == share_link.file_id)
        file_result = await session.execute(file_stmt)
        file = file_result.scalar_one_or_none()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        share_link.download_count += 1
        await session.commit()

        file_path = Path(file.path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on server")

        return FileResponse(
            path=file_path,
            filename=file.original_filename,
            media_type=file.type
        )
