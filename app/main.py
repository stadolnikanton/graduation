# TODO(REFACTOR-LOGGING): Настроить logging вместо print()

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import get_minio_client
from api.v1 import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Выполняется при старте и завершении работы приложения.
    """

    print("🚀 Starting FileCloud application...")

    minio_success = get_minio_client().init_minio(settings.MINIO_BUCKET_NAME)
    if minio_success:
        print(
            f"✅ MinIO bucket '{settings.MINIO_BUCKET_NAME}' initialized successfully"
        )
    else:
        print(f"❌ Failed to initialize MinIO bucket '{settings.MINIO_BUCKET_NAME}'")

    print(f"📊 Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"📁 File storage: MinIO at {settings.MINIO_ENDPOINT}:9000")
    print("✅ Application startup complete")

    yield

    print("🛑 Shutting down FileCloud application...")


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


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
