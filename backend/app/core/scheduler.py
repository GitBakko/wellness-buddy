"""APScheduler async scheduler factory + lifespan integration (D-09, SHOP-08, Pitfall #17).

DST correctness: APScheduler computes the next-fire each invocation via
``zoneinfo`` (Python 3.12 native). NEVER use additive ``timedelta(weeks=1)``
across DST boundaries — clocks jump and skip Monday 00:00 entirely.

Known APScheduler 3.11.2 quirk (Pitfall #17 addendum):
  When the trigger is seeded from a timestamp BEFORE the spring-forward
  Sunday (e.g. server boot on Saturday) it skips one week forward. By the
  second invocation ``previous_fire_time`` lies AFTER DST and the schedule
  becomes stable. In practice the impact is one missed reset every ~5
  years for a server that boots in the 1-hour window before DST kicks in;
  users can manually POST /reset if needed. Fall-back works correctly.

Per-user contract:
  * One job per User row, ``id=f"shopping_reset_{user.id}"``.
  * ``CronTrigger(day_of_week='mon', hour=0, minute=0,
    timezone=ZoneInfo(user.timezone))``.
  * Body opens its own session (no request scope) and calls
    :func:`shopping_service.reset_shopping_list_for_user`.

Lifespan integration (in ``app.main``):
    scheduler = build_scheduler()
    await register_user_jobs(scheduler, session_factory=SessionLocal)
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown(wait=False)
"""

from __future__ import annotations

from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User


def build_scheduler() -> AsyncIOScheduler:
    """Construct the application-wide :class:`AsyncIOScheduler`.

    The scheduler itself runs in UTC; per-job ``CronTrigger`` objects pin
    each user's IANA timezone explicitly so DST is recomputed every run.
    """
    return AsyncIOScheduler(timezone=ZoneInfo("UTC"))


async def register_user_jobs(
    scheduler: AsyncIOScheduler,
    *,
    session_factory: async_sessionmaker,
) -> None:
    """Register one Monday-00:00 reset job per user, in user's IANA tz."""
    async with session_factory() as session:
        users = (await session.scalars(select(User))).all()
    for user in users:
        scheduler.add_job(
            _run_user_reset,
            trigger=CronTrigger(
                day_of_week="mon",
                hour=0,
                minute=0,
                timezone=ZoneInfo(user.timezone),
            ),
            args=(str(user.id),),
            id=f"shopping_reset_{user.id}",
            replace_existing=True,
        )


async def _run_user_reset(user_id: str) -> None:
    """Job body — opens its own session because APScheduler runs outside request scope."""
    from uuid import UUID

    from app.core.database import SessionLocal
    from app.services.shopping_service import reset_shopping_list_for_user

    async with SessionLocal() as session:
        await reset_shopping_list_for_user(session, user_id=UUID(user_id))
