"""Tests for health check, configuration handling, and JSON format compliance."""

import os
import pytest
import respx
import httpx


@pytest.mark.asyncio
async def test_health_endpoint(client: httpx.AsyncClient):
    """Test /health endpoint returns 200 and status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_missing_api_key(client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Test that missing TYPESAFE_API_KEY returns a 500 configuration error."""
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)

    response = await client.get("/choice?input=Hello&choices=a,b")
    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "TypeSafe API key is not configured"}


@pytest.mark.asyncio
@respx.mock
async def test_json_content_type_on_all_responses(client: httpx.AsyncClient):
    """Verify that every successful and error response contains application/json."""
    # 400 Bad Request
    r1 = await client.get("/choice")
    assert r1.headers["content-type"].startswith("application/json")
    assert "error" in r1.json()

    # 404 Not Found
    r2 = await client.get("/nonexistent")
    assert r2.headers["content-type"].startswith("application/json")
    assert "error" in r2.json()

    # 200 Health
    r3 = await client.get("/health")
    assert r3.headers["content-type"].startswith("application/json")
    assert "status" in r3.json()
