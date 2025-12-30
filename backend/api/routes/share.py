from datetime import datetime, timedelta
import secrets
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.db import async_session_maker
from core.deps import get_current_user
from models.file import File as FileModel
from models.user import User
from models.link import ShareLink

router = APIRouter(prefix="/share", tags=["share"])


@router.post("/{file_id}/")
async def create_share_link(
    file_id: int,
    expires_hours: int = Form(24),
    max_downloads: int = Form(1),
    current_user: User = Depends(get_current_user),
):
    async with async_session_maker() as session:
        stmt = select(FileModel).where(
            FileModel.id == file_id, 
            FileModel.owner == current_user.id
        )
        result = await session.execute(stmt)
        file = result.scalar_one_or_none()

        if not file:
            raise HTTPException(
                status_code=404, 
                detail="File not found or access denied"
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        share_link = ShareLink(
            token=token,
            file_id=file_id,
            expires_at=expires_at,
            max_downloads=max_downloads,
            download_count=0,
            created_at=datetime.utcnow()
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


@router.get("/{token}")
async def download_shared_file(token: str):
    async with async_session_maker() as session:
        stmt = select(ShareLink).where(ShareLink.token == token)
        result = await session.execute(stmt)
        share_link = result.scalar_one_or_none()

        if not share_link:
            raise HTTPException(status_code=404, detail="Link not found")

        if share_link.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Link expired")

        if share_link.max_downloads > 0 and share_link.download_count >= share_link.max_downloads:
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
