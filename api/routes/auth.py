from fastapi import APIRouter

from schemas.user import UserBase, UserCreate
from core.secure import hash_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user: UserCreate):
    password = hash_password(user.password)
    print(user)
    return


@router.get("/login")
async def login():
    return {"200": "login"}


@router.get("/logout")
async def logout():
    return {"200": "logout"}

