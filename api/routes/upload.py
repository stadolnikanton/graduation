from fastapi import APIRouter, Depends, HTTPException

from app.db import async_session_maker


router = APIRouter(prefix="/file", tags=["file"])


@router.get("/")
async def get():
    return {"Yeah baby": "It works!"}