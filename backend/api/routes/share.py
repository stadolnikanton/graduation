import secrets
from datetime import datetime, timedelta

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Form, HTTPException, Depends

from app.db import async_session_maker
from core.deps import get_current_user, get_db
from core.minio_client import download_from_minio
from app.config import settings

from models.file import File as FileModel
from models.link import ShareLink
from models.user import User
from api.services.share import Share

router = APIRouter(prefix="/share", tags=["share"])


@router.post("/{file_id}")
async def create_share_link(
    file_id: int,
    expires_hours: int = Form(24),
    max_downloads: int = Form(1),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    share = Share(session)
    return await share.create_share_link(file_id, expires_hours, max_downloads, user)


@router.get("/{token}/info")
async def get_shared_info(token: str, session: AsyncSession = Depends(get_db)):
    share = Share(session)
    return await share.get_shared_info(token)


@router.get("/{token}")
async def download_shared_file(token: str, session: AsyncSession = Depends(get_db)):
    share = Share(session)
    return await share.download_shared_file(token)
