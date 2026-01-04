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

    # JWT
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    
    ACCESS_TOKEN_MAX_AGE: int = 30 * 60 
    REFRESH_TOKEN_MAX_AGE: int = 7 * 24 * 60 * 60  
    HTTPONLY: bool = True
    SECURE: bool = False # В продакшене изменить на True, False только для локальной разработки
    SAME_SITE: str = "lax"
    COOKIE_PATH: str = "/"
    
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
