from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .file import FileDB


class ShareLinkDB(Base):
    __tablename__ = "share_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime] = mapped_column(nullable=True)
    max_downloads: Mapped[int] = mapped_column(default=1, nullable=True)
    download_count: Mapped[int] = mapped_column(default=0, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    file: Mapped["FileDB"] = relationship(
        "FileDB", back_populates="share_links", overlaps="share_links"
    )
