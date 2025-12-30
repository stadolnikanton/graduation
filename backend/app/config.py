import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import Optional


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".env"
        )
    )
    UPLOAD_DIR: str = "static"



settings = Settings()


def get_db_url():
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


def get_files_path():
    if os.path.exists(settings.UPLOAD_DIR):
        return settings.UPLOAD_DIR
    
    else:
        os.mkdir(settings.UPLOAD_DIR)
        return settings.UPLOAD_DIR