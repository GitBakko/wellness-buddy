"""WorkoutLog model (MOD-05, MOD-10).

Always private — never shared with the group regardless of any visibility setting (CONV-14).
Indexed `(user_id, date)` for fast time-series queries on /weight + dashboards.
"""

from __future__ import annotations

from datetime import date as DateType
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampTZ


class WorkoutLog(Base):
    __tablename__ = "workout_log"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    trained: Mapped[bool] = mapped_column(default=False, nullable=False)
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories_burned: Mapped[int | None] = mapped_column(Integer, nullable=True)
    workout_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[TimestampTZ]
    updated_at: Mapped[TimestampTZ]

    __table_args__ = (
        # MOD-10: index time-series workout queries
        Index("ix_workout_user_date", "user_id", "date"),
    )
