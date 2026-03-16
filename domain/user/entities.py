from dataclasses import dataclass
from datetime import datetime


class User(dataclass):
    id: int | None = None
    firstname: str = ""
    lastname: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    created_at: datetime | None = None
