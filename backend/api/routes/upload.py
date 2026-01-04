import os
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, delete


from app.config import get_files_path
from app.db import async_session_maker

from core.deps import get_current_user

from models.file import FileShares, File as FileModel
from models.user import User
from models.link import ShareLink


router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = get_files_path()



@router.get("/")
async def get_files_user(user: User = Depends(get_current_user)):
    async with async_session_maker() as session:
        # 1. Собственные файлы пользователя
        result = await session.execute(
            select(FileModel)
            .where(FileModel.owner == user.id)
            .order_by(FileModel.created_at.desc())
        )
        owned_files_result = result.scalars().all()
        
        ownded_files = []
        for file in owned_files_result:
            ownded_files.append({
                "id": file.id,
                "name": file.name,
                "original_filename": file.original_filename,
                "type": file.type,
                "size": file.size,
                "created_at": file.created_at.isoformat() if file.created_at else None,
                "download_url": f"/files/{file.id}/download",
                "is_owner": True,
                "shared_file": False
            })
        
        # 2. Файлы, к которым пользователю предоставили доступ
        result = await session.execute(
            select(FileModel)
            .join(FileShares, FileModel.id == FileShares.file_id)
            .where(FileShares.user_id == user.id)
            .order_by(FileShares.shared_at.desc())
        )
        shared_files_result = result.scalars().all()
        
        shared_files = []
        for file in shared_files_result:
            shared_files.append({
                "id": file.id,
                "name": file.name,
                "original_filename": file.original_filename,
                "type": file.type,
                "size": file.size,
                "created_at": file.created_at.isoformat() if file.created_at else None,
                "download_url": f"/files/{file.id}/download",
                "is_owner": False,
                "shared_file": True
            })
    
    return {
        "files": {
            "owned": ownded_files,
            "shared": shared_files
        },
        "counts": {
            "owned": len(ownded_files),
            "shared": len(shared_files),
            "total": len(ownded_files) + len(shared_files)
        }
    }


# TODO: Добавить доступ к файлам другим пользователям
@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    user: User = Depends(get_current_user)
):

    async with async_session_maker() as session:
        result = await session.execute(select(FileModel).where(FileModel.id == file_id))
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise HTTPException(404, "Файл не найден")

        if db_file.owner != user.id:
            raise HTTPException(403, "Нет доступа к файлу")

    file_path = Path(db_file.path)
    if not file_path.exists():
        raise HTTPException(404, "Файл отсутствует на сервере")

    return FileResponse(
        path=file_path, filename=db_file.original_filename, media_type=db_file.type
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    user: User = Depends(get_current_user)
):
    async with async_session_maker() as session:
        file = await session.get(FileModel, file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file.owner != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        
        delete_links_stmt = delete(ShareLink).where(ShareLink.file_id == file_id)
        await session.execute(delete_links_stmt)
        
        
        file_path = Path(file.path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to delete file from disk: {str(e)}"
                )
        
        await session.delete(file)
        await session.commit()
        
        return {
            "status": "success",
            "message": "File and all associated share links deleted successfully",
            "file_id": file_id
        }

# FIXME: Исправить ошибку загрузки одинаковых файлов
@router.post("/upload/", response_model=None)
async def create_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):

    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(UPLOAD_DIR) / unique_filename

    content = await file.read()
    file_path.write_bytes(content)

    file_data = {
        "name": unique_filename,
        "original_filename": file.filename,
        "type": file.content_type,
        "owner": user.id,
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
        "download_url": f"/files/{db_file.id}/download",
    }


@router.post("/upload/multiple")
async def create_files(
    files: List[UploadFile] = File(...),
    user: User = Depends(get_current_user)
):
    
    results = []
    
    for file in files:
        try:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = Path(UPLOAD_DIR) / unique_filename
            

            content = await file.read()
            file_path.write_bytes(content)
            
            file_data = {
                "name": unique_filename,
                "original_filename": file.filename,
                "type": file.content_type,
                "owner": user.id,
                "path": str(file_path),
                "size": len(content),
            }
            
            async with async_session_maker() as session:
                db_file = FileModel(**file_data)
                session.add(db_file)
                await session.commit()
                await session.refresh(db_file)
                
                results.append({
                    "status": "success",
                    "file_id": db_file.id,
                    "filename": file.filename,
                    "saved_as": unique_filename,
                    "size": len(content),
                    "download_url": f"/files/{db_file.id}/download"
                })
                
        except Exception as e:
            results.append({
                "status": "error",
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "total_files": len(files),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "files": results
    }
