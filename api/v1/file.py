from fastapi import APIRouter, Depends, File, UploadFile

from domain.file.services import FileUploadService
from domain.user.entities import User

from api.deps import get_current_user, get_file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=None)
async def create_file(
        file: UploadFile = File(...),
        user: User = Depends(get_current_user),
        file_service: FileUploadService = Depends(get_file_service)
):
    return await file_service.file_upload(file, user)