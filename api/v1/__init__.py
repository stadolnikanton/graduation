from fastapi import APIRouter

from api.v1 import auth, default, file

router = APIRouter(prefix="/v1", tags=["version 1"])

for module in [auth, default, file]:
    router.include_router(module.router)
