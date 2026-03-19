import io
import logging
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self, host: str, port: str, user: str, password: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def __get_url(self):
        return f"http://{self.host}:{self.port}"

    def client(self):
        return boto3.client(
            "s3",
            endpoint_url=self.__get_url(),
            aws_access_key_id=self.user,
            aws_secret_access_key=self.password,
            region_name="us-east-1",
            config=boto3.session.Config(signature_version="s3v4"),
        )

    def ensure_bucket_exist(self, bucket_name: str) -> bool:
        try:
            s3 = self.client()
            s3.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404" or error_code == "NoSuchBucket":
                try:
                    s3.create_bucket(Bucket=bucket_name)
                    logger.info(f"Bucket '{bucket_name}' created successfully")
                    return True
                except Exception as e:
                    logger.error(f"Failed to create bucket: {e}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise

    def upload_file(self, file, file_name: str, bucket_name: str) -> bool:
        try:
            s3 = self.client()
            file.file.seek(0)

            s3.upload_fileobj(
                file.file,
                bucket_name,
                file_name,
                ExtraArgs={
                    "ContentType": file.content_type or "application/octet-stream"
                },
            )
            logger.info(
                f"File '{file_name}' uploaded successfully to bucket '{bucket_name}'"
            )
            return True
        except ClientError as e:
            logger.error(f"ClientError uploading file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def download_from_minio(
        self, filename: str, bucket_name: str, original_filename: str
    ):
        try:
            s3 = self.client()
            fileobj = io.BytesIO()

            s3.download_fileobj(bucket_name, filename, fileobj)
            fileobj.seek(0)

            download_filename = original_filename if original_filename else filename
            safe_filename = quote(download_filename)

            try:
                response = s3.head_object(Bucket=bucket_name, Key=filename)
                content_type = response.get("ContentType", "application/octet-stream")
            except:
                content_type = "application/octet-stream"

            return StreamingResponse(
                fileobj,
                media_type=content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{safe_filename}"',
                    "Access-Control-Expose-Headers": "Content-Disposition",
                },
            )
        except ClientError as e:
            logger.error(f"ClientError downloading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def delete_from_minio(self, filename: str, bucket_name: str) -> bool:
        try:
            s3 = self.client()
            s3.delete_object(Bucket=bucket_name, Key=filename)
            logger.info(f"File '{filename}' deleted from bucket '{bucket_name}'")
            return True
        except ClientError as e:
            logger.error(f"ClientError deleting file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    def init_minio(self, bucket: str) -> bool:
        try:
            bucket_name = bucket
            logger.info(f"Initializing MinIO bucket: {bucket_name}")
            self.ensure_bucket_exist(bucket_name)
            logger.info(f"MinIO bucket '{bucket_name}' is ready")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {e}")
            return False
