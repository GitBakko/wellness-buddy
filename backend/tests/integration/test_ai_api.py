"""AI API integration tests — T-AI-01, AI-04, AUTH-12 envelope.

Verifies:
1. /api/ai/_provider_probe (test-only, no auth) returns NullProvider class.
2. The 4 real AI endpoints sit behind `Depends(get_current_user)`. Hitting them
   without a Bearer token returns 401 with the AUTH-12 envelope shape
   ({detail, code}). Plan 03 replaced 02a's 501 stub with the real JWT dependency,
   so 401 (no_token) is the gate now. The 501 ai_unavailable surface from
   NullProvider only appears with a valid Bearer token bound — covered by Plan 04+.

NOTE: Plan 02a's register_exception_handlers flattens AppException's
detail dict into the top-level response body, so the AUTH-12 envelope
appears as `{detail: <str>, code: <str>}` directly (not nested).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _assert_envelope(body: dict[str, object]) -> None:
    """AUTH-12 envelope: top-level {detail: str, code: str} per Plan 02a's handler."""
    assert "detail" in body
    assert "code" in body
    assert isinstance(body["detail"], str)
    assert isinstance(body["code"], str)


def test_provider_probe_returns_null_provider() -> None:
    with TestClient(app) as client:
        r = client.get("/api/ai/_provider_probe")
        assert r.status_code == 200
        body = r.json()
        assert body["provider"] == "NullProvider"
        assert body["is_available"] is False


def test_meal_suggestion_requires_auth_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/meal-suggestion")
        assert r.status_code == 401
        _assert_envelope(r.json())


def test_week_analysis_requires_auth_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/week-analysis")
        assert r.status_code == 401
        _assert_envelope(r.json())


def test_shopping_tips_requires_auth_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/shopping-tips")
        assert r.status_code == 401
        _assert_envelope(r.json())


def test_chat_requires_auth_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/chat")
        assert r.status_code == 401
        _assert_envelope(r.json())
