"""Verify /api/health and /version.json contracts (FND-03, FND-06)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        r = client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "build_hash" in body


def test_version_endpoint() -> None:
    with TestClient(app) as client:
        r = client.get("/version.json")
        assert r.status_code == 200
        body = r.json()
        assert "version" in body
        assert "build_hash" in body
