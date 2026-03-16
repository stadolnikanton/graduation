from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .user import UserDB


class BlacklistedToken(Base):
    __tablename__ = "blacklist_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    token_type: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column()
    revoked_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    owner_jwt: Mapped["User"] = relationship(
        "User", back_populates="blacklisted_tokens", overlaps="blacklisted_tokens"
    )

    def __repr__(self) -> str:
        return (
            f"BlacklistedToken(id={self.id!r}, jti={self.jti!r}, "
            f"user_id={self.user_id!r})"
        )
