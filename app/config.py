import logging
from pathlib import Path

import colorlog
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    # Postgres
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="filecloud")
    DB_USER: str = Field(default="filecloud_user")
    DB_PASSWORD: SecretStr = Field(default="filecloud_password")

    # JWT
    SECRET_KEY: SecretStr = Field(default="dev_secret_key_change_in_production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # MinIO
    MINIO_ENDPOINT: str = Field(default="minio")
    MINIO_PORT_API: str = Field(default="9000")
    MINIO_ROOT_USER: str = Field(default="minioadmin")
    MINIO_ROOT_PASSWORD: SecretStr = Field(default="minioadmin")
    MINIO_BUCKET_NAME: str = Field(default="uploads")

    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    MAX_TOTAL_SIZE: int = Field(default=500 * 1024 * 1024)
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024)

    # Logging

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

logging_config: dict = {
    "level": logging.INFO,
    "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
    "handlers": [colorlog.StreamHandler(), logging.FileHandler("app.log")],
}


def get_db_url() -> str:
    """Формирует URL для подключения к базе данных."""
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:"
        f"{settings.DB_PASSWORD.get_secret_value()}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


def download_url() -> str:
    return f"http://{settings.MINIO_ENDPOINT}:{settings.MINIO_PORT_API}/{settings.MINIO_BUCKET_NAME}"
