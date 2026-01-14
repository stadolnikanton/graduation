import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from pydantic import SecretStr


load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")

    # JWT
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # model_config = SettingsConfigDict(
    #     env_file=os.path.join(
    #         os.path.dirname(os.path.abspath(__file__)), "..", ".env"
    #     )
    # )
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
