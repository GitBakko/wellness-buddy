"""Stub endpoint integration tests — verify AUTH-12 envelope contract.

Representative samples across stub routers (auth/plans/today/weight/workout/admin).
Plans 03/04/07 will replace these stubs with real implementations and re-target
these tests at real behavior.

NOTE: Plan 02a's register_exception_handlers flattens dict-typed HTTPException
detail into the top-level body (when it carries a `code` key), so the
AUTH-12 envelope appears flat as `{detail, code}`.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_envelope(body: dict[str, object]) -> None:
    """AUTH-12 envelope: top-level {detail: str, code: str}."""
    assert "detail" in body
    assert "code" in body
    assert isinstance(body["detail"], str)
    assert isinstance(body["code"], str)


def test_auth_login_stub_returns_envelope() -> None:
    r = client.post("/api/auth/login")
    assert r.status_code == 501
    _assert_envelope(r.json())


def test_plans_upload_stub_returns_envelope() -> None:
    r = client.post("/api/plans/upload")
    assert r.status_code == 501
    _assert_envelope(r.json())


def test_today_get_stub_returns_envelope() -> None:
    r = client.get("/api/today")
    assert r.status_code == 501
    _assert_envelope(r.json())


def test_weight_post_stub_returns_envelope() -> None:
    r = client.post("/api/weight")
    assert r.status_code == 501
    _assert_envelope(r.json())


def test_workout_post_stub_returns_envelope() -> None:
    r = client.post("/api/workout")
    assert r.status_code == 501
    _assert_envelope(r.json())


def test_admin_assign_stub_returns_envelope() -> None:
    r = client.post("/api/admin/users/00000000-0000-0000-0000-000000000000/assign-plan")
    assert r.status_code == 501
    _assert_envelope(r.json())
