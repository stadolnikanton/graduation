from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class ShareLink:
    id: int | None = None
    token: str = ""
    file_id: int | None = None
    expires_at: Optional[datetime.datetime] = None
    max_downloads: int | None = None
    download_count: int | None = None
    created_at: Optional[datetime.datetime] = None
