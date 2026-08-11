"""
Tests for the FastAPI backend endpoints.

Uses httpx's TestClient (built into FastAPI) — no running server needed.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ==================================================
# HEALTH CHECK
# ==================================================
def test_health_returns_200():
    """GET /health should return HTTP 200"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status():
    """GET /health should return {status: 'ok'}"""
    response = client.get("/health")
    data = response.json()
    assert data.get("status") == "ok"


def test_home_returns_200():
    """GET / should return a welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# ==================================================
# HISTORY ENDPOINT
# ==================================================
def test_history_returns_200():
    """GET /history should always return 200 (even when no runs exist yet)"""
    response = client.get("/history")
    assert response.status_code == 200


def test_history_returns_runs_list():
    """GET /history response should contain a 'runs' key with a list"""
    response = client.get("/history")
    data = response.json()
    assert "runs" in data
    assert isinstance(data["runs"], list)


# ==================================================
# OPTIMIZE ENDPOINT — VALIDATION
# ==================================================
def test_optimize_rejects_non_excel():
    """POST /optimize should return 400 if a non-Excel file is uploaded"""
    response = client.post(
        "/optimize",
        files={"file": ("data.csv", b"col1,col2\n1,2", "text/csv")}
    )
    assert response.status_code == 400
