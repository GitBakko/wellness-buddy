"""WeightLog model (MOD-06, MOD-10).

Always private. Numeric(5,2) supports up to 999.99 kg with 0.01 precision.
UNIQUE(user_id, date) prevents duplicate weigh-ins on the same day.
"""

from __future__ import annotations

from datetime import date as DateType
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class WeightLog(Base):
    __tablename__ = "weight_log"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[TimestampTZ]
    updated_at: Mapped[TimestampTZ]

    __table_args__ = (
        # MOD-10: index time-series weight queries
        Index("ix_weight_user_date", "user_id", "date"),
        # One weigh-in per day per user
        UniqueConstraint("user_id", "date", name="uq_weight_user_date"),
    )
