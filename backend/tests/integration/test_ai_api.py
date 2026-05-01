"""AI API integration tests — T-AI-01, AI-04, AUTH-12 envelope.

Verifies:
1. /api/ai/_provider_probe (test-only, no auth) returns NullProvider class.
2. The 4 real AI endpoints return 501 with the AUTH-12 envelope shape
   ({detail, code}). With NullProvider currently bound, the response surface
   is the 501 from the auth dependency stub (auth_not_implemented). Once
   Plan 03 wires real auth, this 501 will move to ai_unavailable from the
   NullProvider — but the envelope shape remains identical.

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


def test_meal_suggestion_returns_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/meal-suggestion")
        assert r.status_code == 501
        _assert_envelope(r.json())


def test_week_analysis_returns_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/week-analysis")
        assert r.status_code == 501
        _assert_envelope(r.json())


def test_shopping_tips_returns_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/shopping-tips")
        assert r.status_code == 501
        _assert_envelope(r.json())


def test_chat_returns_envelope() -> None:
    with TestClient(app) as client:
        r = client.post("/api/ai/chat")
        assert r.status_code == 501
        _assert_envelope(r.json())
