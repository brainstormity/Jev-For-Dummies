"""Tests for the GET /noul endpoint."""

import pytest
import respx
import httpx


@pytest.mark.asyncio
@respx.mock
async def test_valid_noul_true(client: httpx.AsyncClient):
    """Test valid Noul query resulting in true."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "noul_q": {
                    "type": "noul",
                    "noul": 0.98,
                }
            },
            "usage": {"input_tokens": 80, "output_tokens": 15},
        },
    )

    response = await client.get("/noul?input=Win+a+free+iPhone&question=Is+this+spam?")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] is True


@pytest.mark.asyncio
@respx.mock
async def test_valid_noul_false(client: httpx.AsyncClient):
    """Test valid Noul query resulting in false."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "noul_q": {
                    "type": "noul",
                    "noul": 0.04,
                }
            },
        },
    )

    response = await client.get("/noul?input=This+is+a+normal+message&question=Is+this+spam?")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] is False


@pytest.mark.asyncio
@respx.mock
async def test_noul_with_confidence_metadata(client: httpx.AsyncClient):
    """Test Noul query when Jev provides confidence metadata."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "noul_q": {
                    "type": "noul",
                    "noul": 0.97,
                    "confidence": 0.97,
                }
            },
        },
    )

    response = await client.get("/noul?input=Win+a+free+iPhone&question=Is+this+spam?")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] is True
    assert data["confidence"] == 0.97


@pytest.mark.asyncio
async def test_missing_input(client: httpx.AsyncClient):
    """Test error when input query parameter is missing."""
    response = await client.get("/noul?question=Is+this+spam?")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "input is required"}


@pytest.mark.asyncio
async def test_missing_question(client: httpx.AsyncClient):
    """Test error when question query parameter is missing."""
    response = await client.get("/noul?input=Win+a+free+iPhone")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "question is required"}


@pytest.mark.asyncio
@respx.mock
async def test_upstream_jev_error(client: httpx.AsyncClient):
    """Test error handling on upstream Jev error."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=401,
        json={"error": "Unauthorized"},
    )

    response = await client.get("/noul?input=Test&question=Test?")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "Jev authentication failed"}

