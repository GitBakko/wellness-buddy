"""APScheduler weekly-reset cron tests (Pattern 5, Pitfall #17).

Plan 02-05 Task 2 — RED phase.

DST correctness is the key invariant: ``CronTrigger`` with
``timezone=ZoneInfo(user.timezone)`` recomputes next-fire each invocation, so
the Monday 00:00 reset job lands on the right wall-clock minute on both
spring-forward (last Sun of March) and fall-back (last Sun of October)
boundaries. This test set is pure (no DB / no event loop) so it pins the
trigger contract regardless of how :func:`build_scheduler` evolves.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger


def test_dst_spring_forward_2026() -> None:
    """2026 last-Sunday-of-March = March 29 — clocks jump 02:00 → 03:00.

    A trigger fired from ``2026-03-28 23:59 Rome`` must yield
    ``2026-03-30 00:00 Rome`` (Monday after the spring-forward Sunday).
    """
    rome = ZoneInfo("Europe/Rome")
    trig = CronTrigger(day_of_week="mon", hour=0, minute=0, timezone=rome)
    fire = trig.get_next_fire_time(None, datetime(2026, 3, 28, 23, 59, tzinfo=rome))
    assert fire is not None
    assert fire.year == 2026
    assert fire.month == 3
    assert fire.day == 30
    assert fire.hour == 0
    assert fire.minute == 0


def test_dst_fall_back_2026() -> None:
    """2026 last-Sunday-of-October = October 25 — clocks fall back 03:00 → 02:00.

    Fired from ``2026-10-24 23:59 Rome`` → must land on ``2026-10-26 00:00 Rome``.
    """
    rome = ZoneInfo("Europe/Rome")
    trig = CronTrigger(day_of_week="mon", hour=0, minute=0, timezone=rome)
    fire = trig.get_next_fire_time(None, datetime(2026, 10, 24, 23, 59, tzinfo=rome))
    assert fire is not None
    assert fire.year == 2026
    assert fire.month == 10
    assert fire.day == 26
    assert fire.hour == 0
    assert fire.minute == 0


def test_cron_correct_day_of_week_lunedi() -> None:
    """Reset job MUST fire on Monday (Python ``weekday() == 0``)."""
    rome = ZoneInfo("Europe/Rome")
    trig = CronTrigger(day_of_week="mon", hour=0, minute=0, timezone=rome)
    fire = trig.get_next_fire_time(None, datetime(2026, 5, 6, 12, 0, tzinfo=rome))
    assert fire is not None
    assert fire.weekday() == 0  # Monday


def test_build_scheduler_returns_async_io_scheduler() -> None:
    """Factory exposes a configured ``AsyncIOScheduler`` ready for lifespan binding."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    from app.core.scheduler import build_scheduler

    sched = build_scheduler()
    assert isinstance(sched, AsyncIOScheduler)


def test_register_user_jobs_signature() -> None:
    """``register_user_jobs`` is an async function taking scheduler + session_factory."""
    import inspect

    from app.core.scheduler import register_user_jobs

    assert inspect.iscoroutinefunction(register_user_jobs)
    sig = inspect.signature(register_user_jobs)
    # First positional param = scheduler; ``session_factory`` is keyword-only.
    assert "session_factory" in sig.parameters
