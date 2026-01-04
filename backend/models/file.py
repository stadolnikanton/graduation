import enum

from datetime import datetime, timezone

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from models.user import User


class AccessLevel(enum.Enum):
    READ = "read"
    WRITE = "write"
    MANAGE = "manage"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(), nullable=False)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    path: Mapped[str] = mapped_column(String(), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    owner_user: Mapped["User"] = relationship("User", back_populates="files")
    
    share_links: Mapped[list["ShareLink"]] = relationship(
        "ShareLink", 
        back_populates="file",
        cascade="all, delete-orphan",  
        passive_deletes=True
    )

    shared_with: Mapped[list["FileShares"]] = relationship(
        "FileShares", 
        back_populates="file",
        foreign_keys="FileShares.file_id",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    shares_by_me: Mapped[list["FileShares"]] = relationship(
        "FileShares",
        back_populates="owner_user_rel",
        foreign_keys="FileShares.owner_id"
    )


class FileShares(Base):
    __tablename__ = "file_shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey(File.id))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    shared_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    access_level: Mapped[AccessLevel] = mapped_column(
        Enum(AccessLevel), 
        default=AccessLevel.READ, 
        nullable=False
    )

    file: Mapped["File"] = relationship("File", back_populates="shared_with")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    owner_user_rel: Mapped["User"] = relationship("User", foreign_keys=[owner_id])