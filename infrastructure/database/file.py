from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from .link import ShareLinkDB
    from .user import UserDB


class FileDB(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    hash_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=False
    )
    type: Mapped[str] = mapped_column(String(), nullable=False)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    path: Mapped[str] = mapped_column(String(), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    owner_user: Mapped["UserDB"] = relationship("UserDB", back_populates="files")

    share_links: Mapped[list["ShareLinkDB"]] = relationship(
        "ShareLinkDB",
        back_populates="file",
        overlaps="file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    shares: Mapped[list["FileSharesDB"]] = relationship(
        "FileSharesDB",
        back_populates="file",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class FileSharesDB(Base):
    __tablename__ = "file_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    shared_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    file: Mapped["FileDB"] = relationship("FileDB", back_populates="shares")
    owner_user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[owner_id])
    shared_user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])
