import os
import uuid
import anyio
from fastapi import UploadFile
from domain.errors import FileSizeExceededError, FileAlreadyExistsError, FileUploadError
from domain.user.entities import User
from domain.file.entities import File
from app.config import settings
from infrastructure.minio.client import  MinioClient
from infrastructure.repositories.file import FileRepository


class FileUploadService:
    def __init__(self, minio_client: MinioClient, file_repo: FileRepository):
        self.minio_client = minio_client
        self.file_repo = file_repo
        self.MAX_TOTAL_SIZE = 500 * 1024 * 1024
        self.MAX_FILE_SIZE = 100 * 1024 * 1024

    async def file_upload(self, file: UploadFile, user: User):
        if file.size > self.MAX_FILE_SIZE:
            raise FileSizeExceededError()

        type = os.path.splitext(file.filename)[1].lower()
        hash_name = f"{uuid.uuid4()}{type}"
        file_path = f"http://{settings.MINIO_ENDPOINT}:9000/{settings.MINIO_BUCKET_NAME}/{hash_name}"

        self.minio_client.ensure_bucket_exist(settings.MINIO_BUCKET_NAME)

        result = await self.file_repo.file_exists_for_user(file.filename, int(user.id))

        if result:
            raise FileAlreadyExistsError(file.filename)

        await file.seek(0)

        success = await anyio.to_thread.run_sync(
            self.minio_client.upload_file, file, hash_name, settings.MINIO_BUCKET_NAME
        )

        if not success:
            raise FileUploadError()


        file = File(
            hash_name=hash_name,
            original_filename=file.filename,
            type=type,
            owner=user.id,
            path=file_path,
            size=file.size
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
