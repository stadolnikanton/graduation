import os
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError


from app.config import get_files_path
from app.db import async_session_maker

from core.deps import get_current_user

from schemas.file import ShareRequest

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


@router.post("/{file_id}/share")
async def grant_file_access(
    data: ShareRequest,
    file_id: int,
    user: User = Depends(get_current_user),
):
    async with async_session_maker() as session:
        result = await session.execute(select(FileModel).where(FileModel.id == file_id))
        db_file = result.scalar_one_or_none()

        if not db_file:
            raise HTTPException(404, "Файл не найден")

        if db_file.owner != user.id:
            raise HTTPException(403, "Нет доступа к файлу")
        
        if data.user_id == user.id:
            raise HTTPException(400, "Нельзя поделиться с самим собой")
        
        result = await session.execute(
            select(User).where(User.id == data.user_id)
        )
        recipient = result.scalar_one_or_none()

        if not recipient:
            raise HTTPException(404, "Пользователь-получатель не найден")
        
        result = await session.execute(
            select(FileShares).where(
                FileShares.file_id == file_id,
                FileShares.user_id == data.user_id
            )
        )
        existing_share = result.scalar_one_or_none()
        
        if existing_share:
            raise HTTPException(409, "Доступ уже предоставлен этому пользователю")
        
        try:
            new_share = FileShares(
                file_id=file_id,
                user_id=data.user_id,
                owner_id=user.id,
                access_level=data.access_level
            )
            
            session.add(new_share)
            await session.commit()
            await session.refresh(new_share)
            
            return {
                "message": "Доступ успешно предоставлен",
                "share_id": new_share.id,
                "file_id": file_id,
                "recipient_id": data.user_id,
                "access_level": data.access_level
            }
            
        except IntegrityError:
            await session.rollback()
            raise HTTPException(500, "Ошибка при предоставлении доступа")


@router.get("/{file_id}/shared-users")
async def get_shared_users(
        file_id: int, 
        current_user: User = Depends(get_current_user)
):
    async with async_session_maker() as session:
        result = await session.execute(
            select(FileShares.user_id, FileShares.access_level)
            .where(FileShares.file_id == file_id)
        )
        shared_records = result.all()
        
        if not shared_records:
            return []
        
        user_ids = [record.user_id for record in shared_records]
        
        users_result = await session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = users_result.scalars().all()

        users_dict = {user.id: user for user in users}
        
        response = []
        for record in shared_records:
            user = users_dict.get(record.user_id)
            if user:
                response.append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "access_level": record.access_level
                })
        
        return response


@router.delete("/{file_id}/share/{user_id}")
async def remove_file_share(
    file_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
):
    async with async_session_maker() as session:
        result = await session.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        db_file = result.scalar_one_or_none()
        
        if not db_file:
            raise HTTPException(404, "Файл не найден")
        
        if db_file.owner != user.id:
            raise HTTPException(403, "Вы не владелец этого файла")
        
        if user_id == user.id:
            raise HTTPException(400, "Нельзя удалить доступ самому себе")
        
        result = await session.execute(
            select(FileShares).where(
                FileShares.file_id == file_id,
                FileShares.user_id == user_id
            )
        )
        file_share = result.scalar_one_or_none()
        
        if not file_share:
            raise HTTPException(404, "Доступ не найден")
        
        await session.delete(file_share)
        await session.commit()
        
        return {
            "message": "Доступ успешно удален",
            "file_id": file_id,
            "removed_user_id": user_id
        }


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

        if db_file.owner == user.id:
            raise HTTPException(403, "Нет доступа к файлу")
        else:
            result = await session.execute(
                select(FileShares).where(
                    FileShares.file_id == file_id,
                    FileShares.user_id == user.id
                )
            )
            access_file = result.scalar_one_or_none()
            
            if not access_file:
                raise HTTPException(403, "Нет доступа к файлу")

    file_path = Path(db_file.path)
    if not file_path.exists():
        raise HTTPException(404, "Файл отсутствует на сервере")

    return FileResponse(
        path=file_path, 
        filename=db_file.original_filename, 
        media_type=db_file.type
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


@router.post("/upload")
async def create_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    MAX_FILE_SIZE = 100 * 1024 * 1024
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(UPLOAD_DIR) / unique_filename
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(FileModel).where(
                FileModel.owner == user.id,
                FileModel.original_filename == file.filename
            )
        )
        existing_file = result.scalar_one_or_none()
        
        if existing_file:
            raise HTTPException(409, f"Файл с именем '{file.filename}' уже существует у вас")
        
        file_path.write_bytes(content)
        
        file_data = {
            "name": unique_filename,
            "original_filename": file.filename,
            "type": file.content_type or "application/octet-stream",
            "owner": user.id,
            "path": str(file_path),
            "size": len(content),
        }
        
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
    MAX_TOTAL_SIZE = 500 * 1024 * 1024
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    total_size = 0
    results = []
    
    for file in files:
        content = await file.read()
        await file.seek(0) 

        if len(content) > MAX_FILE_SIZE:
            results.append({
                "status": "error",
                "filename": file.filename,
                "error": f"Файл слишком большой. Максимум: {MAX_FILE_SIZE // (1024*1024)}MB"
            })
            continue
        
        total_size += len(content)
        
        file_extension = os.path.splitext(file.filename)[1].lower()

    
    if total_size > MAX_TOTAL_SIZE:
        raise HTTPException(413, f"Общий размер файлов превышает {MAX_TOTAL_SIZE // (1024*1024)}MB")
    
    for file in files:
        try:
            if any(r.get("filename") == file.filename and r["status"] == "error" for r in results):
                continue
            
            content = await file.read()
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = Path(UPLOAD_DIR) / unique_filename
            
            async with async_session_maker() as session:
                result = await session.execute(
                    select(FileModel).where(
                        FileModel.owner == user.id,
                        FileModel.original_filename == file.filename
                    )
                )
                existing_file = result.scalar_one_or_none()
                
                if existing_file:
                    base_name = os.path.splitext(file.filename)[0]
                    counter = 1
                    new_filename = f"{base_name} ({counter}){file_extension}"
                    
                    while True:
                        result = await session.execute(
                            select(FileModel).where(
                                FileModel.owner == user.id,
                                FileModel.original_filename == new_filename
                            )
                        )
                        if not result.scalar_one_or_none():
                            break
                        counter += 1
                        new_filename = f"{base_name} ({counter}){file_extension}"
                    
                    file.filename = new_filename
            
            file_path.write_bytes(content)
            
            file_data = {
                "name": unique_filename,
                "original_filename": file.filename,
                "type": file.content_type or "application/octet-stream",
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
                    "original_name": file.filename,
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
