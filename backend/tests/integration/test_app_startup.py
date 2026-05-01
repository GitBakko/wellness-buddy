"""Smoke test: app imports cleanly, lifespan runs, base routes registered.

AI provider binding check is owned by Plan 02b's `test_ai_api`. Plan 02a only verifies
that the app boots with the lifespan stub (configure_logging executed without error).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_app_imports_and_routes_registered() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/health" in paths
    assert "/version.json" in paths
    assert "/api/errors" in paths


def test_app_boots_with_lifespan() -> None:
    with TestClient(app) as client:
        # TestClient context-manager triggers lifespan. If configure_logging raises, this fails.
        r = client.get("/api/health")
        assert r.status_code == 200
