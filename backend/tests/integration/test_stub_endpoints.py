"""Stub endpoint integration tests — verify AUTH-12 envelope contract.

Representative samples across stub routers (auth/plans/today/weight/workout/admin).
Plans 03/04/07 will replace these stubs with real implementations and re-target
these tests at real behavior.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_envelope(body: dict[str, object]) -> None:
    """The AUTH-12 envelope is `{detail: <obj-or-str>, ...}`. Our stubs nest the
    structured payload under `detail`, so we check both top-level shape and
    nested {detail, code} contract."""
    assert "detail" in body
    detail = body["detail"]
    assert isinstance(detail, dict)
    assert "detail" in detail
    assert "code" in detail


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
