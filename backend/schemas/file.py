from enum import Enum

from pydantic import BaseModel, ConfigDict


class FileId(BaseModel):
    id: int


class FileResponseSchema(BaseModel):
    status: str
    file_id: int
    filename: str
    saved_as: str
    size: int
    download_url: str

    model_config = ConfigDict(from_attributes=True)


class ShareRequest(BaseModel):
    user_id: int
    access_level: str = "read"


class AccessLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    MANAGE = "manage"
