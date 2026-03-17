import logging
from contextlib import asynccontextmanager

import colorlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import get_minio_client
from api.exceptions import register_exception_handlers
from api.v1 import router
from app.config import settings

console_handler = colorlog.StreamHandler()
console_handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logger = logging.getLogger("filecloud")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Выполняется при старте и завершении работы приложения.
    """
    logger.info("🚀 Starting FileCloud application...")

    minio_success = get_minio_client().init_minio(settings.MINIO_BUCKET_NAME)
    if minio_success:
        logger.info(
            f"✅ MinIO bucket '{settings.MINIO_BUCKET_NAME}' initialized successfully"
        )
    else:
        logger.error(
            f"❌ Failed to initialize MinIO bucket '{settings.MINIO_BUCKET_NAME}'"
        )

    logger.info(
        f"📊 Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    logger.info(f"📁 File storage: MinIO at {settings.MINIO_ENDPOINT}:9000")
    logger.info("✅ Application startup complete")

    yield

    logger.info("🛑 Shutting down FileCloud application...")


app = FastAPI(
    title="FileCloud API",
    description="Cloud file storage and sharing service",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://frontend:80",
        "https://cloud.stadolnik.site",
        "https://api.stadolnik.site",
        "https://stadolnik.site",
        "http://cloud.stadolnik.site",
        "http://api.stadolnik.site",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


register_exception_handlers(app)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
