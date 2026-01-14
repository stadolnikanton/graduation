"""Инициализирует MinIO bucket при старте приложения"""
import logging
from .minio_client import ensure_bucket_exists
from app.config import settings

logger = logging.getLogger(__name__)

def init_minio():
    try:
        bucket_name = settings.MINIO_BUCKET_NAME
        logger.info(f"Initializing MinIO bucket: {bucket_name}")
        ensure_bucket_exists(bucket_name)
        logger.info(f"MinIO bucket '{bucket_name}' is ready")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        return False