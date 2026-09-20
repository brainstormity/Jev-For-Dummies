"""Tests for the GET /score endpoint."""

import pytest
import respx
import httpx


@pytest.mark.asyncio
@respx.mock
async def test_valid_score_0_to_10(client: httpx.AsyncClient):
    """Test valid Score request on a 0 to 10 scale returning 8."""
    # Jev maps scale into 10 levels (0 to 9 index), score ~ 7.2 yields 8 out of 10
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "score_q": {
                    "type": "score",
                    "score": 7.2,
                    "confidence": 0.89,
                    "legend": {str(i): str(i) for i in range(10)},
                    "probabilities": {str(i): 0.1 for i in range(10)},
                }
            },
            "usage": {"input_tokens": 120, "output_tokens": 20},
        },
    )

    response = await client.get(
        "/score?input=This+user+is+extremely+toxic&question=How+toxic+is+this?&min=0&max=10"
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] == 8
    assert data["confidence"] == 0.89
    assert isinstance(data["probabilities"], dict)


@pytest.mark.asyncio
@respx.mock
async def test_valid_score_custom_scale(client: httpx.AsyncClient):
    """Test valid Score on custom scale min=1, max=5."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "score_q": {
                    "type": "score",
                    "score": 2.0,  # on 5 levels (0..4), 2 is middle, so 1 + (2/4)*4 = 3
                    "confidence": 0.95,
                    "probabilities": {"2": 1.0},
                }
            },
        },
    )

    response = await client.get(
        "/score?input=Neutral+customer+feedback&question=Rate+sentiment&min=1&max=5"
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] == 3
    assert data["confidence"] == 0.95


@pytest.mark.asyncio
async def test_missing_input(client: httpx.AsyncClient):
    """Test error when input query parameter is missing."""
    response = await client.get("/score?question=How+toxic?&min=0&max=10")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "input is required"}


@pytest.mark.asyncio
async def test_missing_question(client: httpx.AsyncClient):
    """Test error when question query parameter is missing."""
    response = await client.get("/score?input=Toxic&min=0&max=10")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "question is required"}


@pytest.mark.asyncio
async def test_missing_min(client: httpx.AsyncClient):
    """Test error when min query parameter is missing."""
    response = await client.get("/score?input=Toxic&question=How+toxic?&max=10")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "min is required"}


@pytest.mark.asyncio
async def test_missing_max(client: httpx.AsyncClient):
    """Test error when max query parameter is missing."""
    response = await client.get("/score?input=Toxic&question=How+toxic?&min=0")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "max is required"}


@pytest.mark.asyncio
async def test_invalid_min_non_integer(client: httpx.AsyncClient):
    """Test error when min is not an integer."""
    response = await client.get("/score?input=Toxic&question=How+toxic?&min=abc&max=10")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "min must be an integer"}


@pytest.mark.asyncio
async def test_invalid_max_non_integer(client: httpx.AsyncClient):
    """Test error when max is not an integer."""
    response = await client.get("/score?input=Toxic&question=How+toxic?&min=0&max=xyz")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "max must be an integer"}


@pytest.mark.asyncio
async def test_max_less_than_or_equal_to_min(client: httpx.AsyncClient):
    """Test error when max <= min."""
    response = await client.get("/score?input=Toxic&question=How+toxic?&min=5&max=5")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "max must be greater than min"}

    response2 = await client.get("/score?input=Toxic&question=How+toxic?&min=10&max=0")
    assert response2.status_code == 400
    assert response2.json() == {"error": "max must be greater than min"}


@pytest.mark.asyncio
@respx.mock
async def test_upstream_jev_error(client: httpx.AsyncClient):
    """Test error handling when Jev returns an upstream failure."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=429,
        json={"error": "Rate limit exceeded"},
    )

    response = await client.get("/score?input=Toxic&question=How+toxic?&min=0&max=10")
    assert response.status_code == 429
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "Jev rate limit exceeded"}

