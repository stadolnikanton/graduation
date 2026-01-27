from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .file import File
    from .token import BlacklistedToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(), nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="owner_user",
        lazy="select",
        cascade="all, delete-orphan",
    )

    blacklisted_tokens: Mapped[list["BlacklistedToken"]] = relationship(
        "BlacklistedToken",
        back_populates="owner_jwt",
        overlaps="owner_jwt",
        lazy="select",
        cascade="all, delete-orphan",
    )

    shared_files_access = relationship(
        "FileShares",
        foreign_keys="[FileShares.user_id]",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"
