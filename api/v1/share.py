import logging
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile

from domain.file.services import FileUploadService
from domain.user.entities import User

from api.deps import get_current_user, get_file_service

router = APIRouter(prefix="/share", tags=["share"])
logger = logging.getLogger("filecloud.share")