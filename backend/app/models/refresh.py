"""RefreshToken model (AUTH-04..AUTH-08, PITFALLS#4).

Schema only — Plan 03 fills in rotation logic + 10s idempotent grace window.
`family_id` groups all refresh tokens descending from a single login session;
on reuse-after-revoke we revoke the entire family. `cached_access`/`cached_refresh`
hold the new pair for the 10s grace window so concurrent refresh attempts get the
same response (PITFALLS#4 — JWT refresh race).
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    jti: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), unique=True, index=True, nullable=False)
    family_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    replaced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cached_access: Mapped[str | None] = mapped_column(Text, nullable=True)
    cached_refresh: Mapped[str | None] = mapped_column(Text, nullable=True)
    issued_at: Mapped[TimestampTZ]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        # Family-scoped lookups for revocation cascade
        Index("ix_refresh_family", "family_id"),
        Index("ix_refresh_user", "user_id"),
    )
