import os
import io
import boto3
from urllib.parse import quote
from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse
from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}:9000",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY.get_secret_value(),
        region_name="us-east-1",
        config=boto3.session.Config(signature_version='s3v4')
    )


def ensure_bucket_exists(bucket_name):
    try:
        s3 = get_s3_client()
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404" or error_code == "NoSuchBucket":
            try:
                s3.create_bucket(Bucket=bucket_name)
                print(f"Bucket '{bucket_name}' created successfully")
                return True
            except Exception as e:
                print(f"Failed to create bucket: {e}")
                raise
        else:
            print(f"Error checking bucket: {e}")
            raise


def upload_file(file, file_name, bucket_name):
    try:
        s3 = get_s3_client()
        file.file.seek(0)
        
        s3.upload_fileobj(
            file.file, 
            bucket_name, 
            file_name,
            ExtraArgs={'ContentType': file.content_type or 'application/octet-stream'}
        )
        
        print(f"File '{file_name}' uploaded successfully to bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"ClientError uploading file: {e}")
        return False
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def download_from_minio(filename, bucket_name, original_filename=None):
    try:
        s3 = get_s3_client()
        fileobj = io.BytesIO()
        
        s3.download_fileobj(bucket_name, filename, fileobj)
        fileobj.seek(0)

        download_filename = original_filename if original_filename else filename
        safe_filename = quote(download_filename)

        try:
            response = s3.head_object(Bucket=bucket_name, Key=filename)
            content_type = response.get('ContentType', 'application/octet-stream')
        except:
            content_type = 'application/octet-stream'

        return StreamingResponse(
            fileobj,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{safe_filename}\"",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except ClientError as e:
        print(f"ClientError downloading file: {e}")
        return None
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None


def delete_from_minio(filename, bucket_name):
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=bucket_name, Key=filename)
        print(f"File '{filename}' deleted from bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"ClientError deleting file: {e}")
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False