import datetime
import secrets
from datetime import datetime, timedelta


def create_share_token() -> str:
    return secrets.token_urlsafe(32)


def calculate_expires_at(hours: int):
    return datetime.now() + timedelta(hours=hours)
