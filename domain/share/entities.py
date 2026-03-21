from dataclasses import dataclass
import datetime


@dataclass
class ShareLink:
    id: int | None = None
    token: str = ""
    file_id: int | None = None
    expires_at: datetime
    max_downloads: int | None = None
    download_count: int | None = None
    created_at: datetime
