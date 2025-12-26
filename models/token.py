from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklist_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    token_type: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[datetime] = mapped_column()
    revoked_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    reason: Mapped[str] = mapped_column(Text, nullable=True)

    owner_jwt: Mapped["User"] = relationship("User", back_populates="blacklisted_tokens")

    def __repr__(self) -> str:
        return f"BlacklistedToken(id={self.id!r}, jti={self.jti!r}, user_id={self.user_id!r})"
