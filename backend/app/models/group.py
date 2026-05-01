"""Group model (MOD-02).

Phase 1 schema only — family meal sync logic lands Phase 2. Existence in Phase 1 schema
ensures `users.group_id` FK target is available when migrations apply.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampTZ

if TYPE_CHECKING:
    from app.models.user import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[TimestampTZ]

    users: Mapped[list[User]] = relationship(back_populates="group")
