import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    # Postgres
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="filecloud")
    DB_USER: str = Field(default="filecloud_user")
    DB_PASSWORD: SecretStr = Field(default="filecloud_password")

    # JWT
    SECRET_KEY: SecretStr
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # MinIO
    MINIO_ENDPOINT: str = Field(default="minio")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: SecretStr = Field(default="minioadmin")
    MINIO_BUCKET_NAME: str = Field(default="uploads")

    # File storage
    UPLOAD_DIR: str = Field(default="static")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()


def get_db_url() -> str:
    """Формирует URL для подключения к базе данных."""
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:"
        f"{settings.DB_PASSWORD.get_secret_value()}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


def get_files_path() -> str:
    """Возвращает путь к директории для загрузки файлов, создавая её при необходимости."""
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    return upload_dir