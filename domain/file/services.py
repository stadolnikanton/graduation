import os
import uuid
from typing import List

import anyio
from fastapi import UploadFile

from domain.errors import (
    FileSizeExceededError,
    FileAlreadyExistsError,
    FileUploadError,
    FileDeleteError,
    FileNotFoundError,
    FileAccessError,
    FileStorageNotFoundError,
)
from domain.user.entities import User
from domain.file.entities import File
from app.config import settings, download_url
from infrastructure.minio.client import MinioClient
from infrastructure.repositories.file import FileRepository


class FileUploadService:
    def __init__(self, minio_client: MinioClient, file_repo: FileRepository):
        self.minio_client = minio_client
        self.file_repo = file_repo

    async def file_upload(self, file: UploadFile, user: User):
        if file.size > settings.MAX_FILE_SIZE:
            raise FileSizeExceededError()

        file_type = os.path.splitext(file.filename)[1].lower()
        hash_name = f"{uuid.uuid4()}{file_type}"
        file_path = f"{download_url()}/{hash_name}"
        self.minio_client.ensure_bucket_exist(settings.MINIO_BUCKET_NAME)

        result = await self.file_repo.file_by_filename_exists_for_user(
            file.filename, int(user.id)
        )

        if result:
            raise FileAlreadyExistsError()

        await file.seek(0)

        success = await anyio.to_thread.run_sync(
            self.minio_client.upload_file, file, hash_name, settings.MINIO_BUCKET_NAME
        )

        if not success:
            raise FileUploadError()

        file = File(
            hash_name=hash_name,
            original_filename=file.filename,
            type=file_type,
            owner=user.id,
            path=file_path,
            size=file.size,
        )

        new_file = await self.file_repo.create(file)

        return {
            "status": "success",
            "file_id": new_file.id,
            "filename": new_file.original_filename,
            "saved_as": new_file.hash_name,
            "size": new_file.size,
            "download_url": f"/files/{new_file.id}/download",
            "minio_url": new_file.path,
        }

    async def file_multi_upload(self, files: List[File], user: User):
        response = []
        for file in files:
            try:
                result = await self.file_upload(file, user)
                response.append(result)
            except (FileUploadError, FileAlreadyExistsError) as e:
                result = {
                    "status": "error",
                    "filename": file.filename,
                    "size": file.size,
                    "error": e.status_code,
                    "error_message": e.default_message,
                }
            response.append(result)

        return {
            "total_files": len(files),
            "successful": len(
                [file for file in response if file["status"] == "success"]
            ),
            "failed": len([file for file in response if file["status"] == "error"]),
            "files": response,
        }

    async def get_all_file(self, user):
        files = await self.file_repo.get_all_file(user.id)
        return files

    async def file_download(self, file_id, user):
        try:
            file = await self.file_repo.get_by_id(file_id)
            if not file:
                raise FileNotFoundError()
            if file.owner != user.id:
                raise FileAccessError()

            file_response = self.minio_client.download_from_minio(
                file.hash_name, settings.MINIO_BUCKET_NAME, file.original_filename
            )

            if not file_response:
                raise FileStorageNotFoundError(file.original_filename)

            return file_response
        except (FileNotFoundError, FileAccessError) as e:
            return {"status": e.status_code, "message": e.default_message}

    async def file_download_by_id(self, file_id):
        try:
            file = await self.file_repo.get_by_id(file_id)
            if not file:
                raise FileNotFoundError()

            file_response = self.minio_client.download_from_minio(
                file.hash_name, settings.MINIO_BUCKET_NAME, file.original_filename
            )

            if not file_response:
                raise FileStorageNotFoundError(file.original_filename)

            return file_response
        except (FileNotFoundError, FileAccessError) as e:
            return {"status": e.status_code, "message": e.default_message}

    async def file_delete(self, file_id, user):
        try:
            file = await self.file_repo.file_delete(file_id, user.id)

            if not file:
                raise FileNotFoundError()

            result = self.minio_client.delete_from_minio(
                file.hash_name, settings.MINIO_BUCKET_NAME
            )

            if not result:
                raise FileDeleteError()

            return {
                "status": "success",
                "message": "File deleted successfully",
                "file_id": file_id,
            }

        except FileNotFoundError as e:
            return {
                "status": "failed",
                "message": e.default_message,
                "status_code": e.status_code,
                "file_id": file_id,
            }
