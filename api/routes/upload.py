from typing import List

from core.deps import get_current_user, get_db
from fastapi import APIRouter, Depends, File, UploadFile
from models.user import User
from schemas.file import ShareRequest
from sqlalchemy.ext.asyncio import AsyncSession


from api.services.upload import Upload

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/")
async def get_files_user(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
):
    upload = Upload(session)

    return await upload.get_files_user(user)


@router.post("/{file_id}/share")
async def grant_file_access(
    data: ShareRequest,
    file_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    upload = Upload(session)
    return await upload.grant_file_access(data, file_id, user)


@router.get("/{file_id}/shared-users")
async def get_shared_users(file_id: int, session: AsyncSession = Depends(get_db)):
    upload = Upload(session)

    return await upload.get_shared_users(file_id)


@router.delete("/{file_id}/share/{user_id}")
async def remove_file_share(
    file_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    upload = Upload(session)
    return await upload.remove_file_share(file_id, user_id, user)
