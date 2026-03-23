import logging
from fastapi import APIRouter, Depends

from domain.share.services import ShareServices
from domain.user.entities import User

from api.deps import get_current_user, get_share_service

router = APIRouter(prefix="/share", tags=["share"])
logger = logging.getLogger("filecloud.share")


@router.post("/{file_id}")
async def create_share_link(
        file_id: int, 
        expires_at: int | None = None, 
        max_downloads: int | None = None, 
        user: User = Depends(get_current_user),
        share_services: ShareServices = Depends(get_share_service)
        ):
   return await share_services.create_share_link(file_id, user, expires_at, max_downloads) 


@router.delete("/{token}")
async def delete_share_link(
        token: str,
        share_services: ShareServices = Depends(get_share_service) 
        ):
    return await share_services.delete_shared_link(token)


@router.get("/{token}")
async def download_shared_file(token: str, share_services: ShareServices = Depends(get_share_service)):
    return await share_services.download_shared_file(token)


@router.get("/{token}/info")
async def get_shared_info(token: str, share_services: ShareServices = Depends(get_share_service)):
    return await share_services.get_shared_info(token)

