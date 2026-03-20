import logging
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile

from domain.file.services import FileUploadService
from domain.user.entities import User

from api.deps import get_current_user, get_file_service

router = APIRouter(prefix="/files", tags=["files"])
logger = logging.getLogger("filecloud.file")


@router.post("/upload", response_model=None)
async def create_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_service),
):
    logger.info(
        f"File uploaded: {file.filename}, user: {user.first_name} {user.last_name} username: {user.username}"
    )
    return await file_service.file_upload(file, user)


@router.post("/upload/multiple")
async def create_files(
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_service),
):
    logger.info(
        f"Filse uploaded: {[file for file in files]}, user: {user.first_name} {user.last_name} username: {user.username}"
    )
    return await file_service.file_multi_upload(files, user)


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    user: User = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_service),
):
    logger.info(
        f"File deleted: {file_id}, user: {user.first_name} {user.last_name} username: {user.username}"
    )
    return await file_service.file_delete(file_id, user)
