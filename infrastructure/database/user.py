from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .file import File
    from .token import BlacklistedToken


class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

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
        return (
            f"User("
            f"id={self.id!r},"
            f"firstname={self.first_name!r},"
            f"lastname={self.last_name!r},"
            f"username={self.username!r},"
            f"email={self.email!r},"
            f"created_at={self.created_at!r},"
            f")"
        )
