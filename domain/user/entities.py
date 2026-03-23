from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None = None
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: datetime | None = None
