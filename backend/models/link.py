from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ShareLink(Base):
    __tablename__ = "share_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    expires_at: Mapped[datetime]
    max_downloads: Mapped[int] = mapped_column(default=1)
    download_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    file: Mapped["File"] = relationship("File")
