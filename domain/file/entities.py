from dataclasses import dataclass
from datetime import datetime


@dataclass
class File:
    id: int | None = None
    hash_name: str = ""
    original_filename: str = ""
    type: str = ""
    owner: int | None = None
    path: str = ""
    size: int  = 0
    created_at: datetime | None = None


@dataclass
class FileShares:
    id: int | None = None
    file_id: int | None = None
    user_id: int | None = None
    owner_id: int | None = None
    shared_at: datetime | None = None