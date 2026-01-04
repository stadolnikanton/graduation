from pydantic import BaseModel
from enum import Enum

class FileId(BaseModel):
    id: int


class FileResponseSchema(BaseModel):
    status: str
    file_id: int
    filename: str
    saved_as: str
    size: int
    download_url: str

    class Config:
        from_attributes = True


class ShareRequest(BaseModel):
    user_id: int
    access_level: str = "read"


class AccessLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    MANAGE = "manage"