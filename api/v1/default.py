from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="", tags=["default"])


@router.get("/")
async def root():
    return {
        "message": "FileCloud API",
        "version": "1.0.1",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "filecloud",
        "timestamp": f"{datetime.now()}",
    }
