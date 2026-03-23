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
    expires_hours: int | None = None,
    max_downloads: int | None = None,
    user: User = Depends(get_current_user),
    share_services: ShareServices = Depends(get_share_service),
):
    result = await share_services.create_share_link(
        file_id, user, expires_hours, max_downloads
    )
    logger.info(
        f"Share link created: file_id={file_id}, "
        f"token={result.get('token')}, "
        f"expires_hours={expires_hours}, "
        f"max_downloads={max_downloads}"
    )
    return result


@router.delete("/{token}")
async def delete_share_link(
    token: str, share_services: ShareServices = Depends(get_share_service)
):
    result = await share_services.delete_shared_link(token)
    logger.info(f"Share link deleted: token={token}, status={result.get('status')}")
    return result


@router.get("/{token}")
async def download_shared_file(
    token: str, share_services: ShareServices = Depends(get_share_service)
):
    logger.info(f"Share download requested: token={token}")
    return await share_services.download_shared_file(token)


@router.get("/{token}/info")
async def get_shared_info(
    token: str, share_services: ShareServices = Depends(get_share_service)
):
    logger.info(f"Share info requested: token={token}")
    return await share_services.get_shared_info(token)
