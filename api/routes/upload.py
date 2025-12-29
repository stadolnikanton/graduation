import os
import uuid
from pathlib import Path


from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi import File, UploadFile

from core.deps import get_current_user

from models.user import User
from models.file import File as FileModel

from app.db import async_session_maker
from app.config import get_files_path



router = APIRouter(prefix="/files", tags=["files"])


@router.get("/")
async def get():
    return {"Yeah baby": "It works!"}


@router.post("/upload/")
async def create_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    ):

    UPLOAD_DIR = get_files_path()

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"


    file_path = Path(UPLOAD_DIR) / unique_filename

    content = await file.read()
    file_path.write_bytes(content)

    file_data = {
        "name": unique_filename,
        "original_filename": file.filename,
        "type": file.content_type,
        "owner": current_user.id,
        "path": str(file_path),
        "size": len(content),
    }

    async with async_session_maker() as session:
        db_file = FileModel(**file_data)
        session.add(db_file)
        await session.commit()
        await session.refresh(db_file)
    
    return {
        "status": "success",
        "file_id": db_file.id,
        "filename": file.filename,
        "saved_as": unique_filename,
        "size": len(content),
        "download_url": f"/files/{db_file.id}/download"
    }

@router.post("/upload/multiple")
async def create_files():
    pass