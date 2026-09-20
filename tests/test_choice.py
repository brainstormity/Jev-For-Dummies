"""Tests for the GET /choice endpoint."""

import pytest
import respx
import httpx


@pytest.mark.asyncio
@respx.mock
async def test_valid_choice(client: httpx.AsyncClient):
    """Test standard valid choice request with probability and confidence metadata."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "choice_q": {
                    "type": "choice",
                    "choice": "spam",
                    "confidence": 0.94,
                    "probabilities": {
                        "spam": 0.94,
                        "not spam": 0.06,
                    },
                }
            },
            "usage": {"input_tokens": 100, "output_tokens": 10},
        },
    )

    response = await client.get("/choice?input=Win+a+free+iPhone&choices=spam,not+spam")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] == "spam"
    assert data["confidence"] == 0.94
    assert data["probabilities"] == {"spam": 0.94, "not spam": 0.06}


@pytest.mark.asyncio
@respx.mock
async def test_multiple_choices_and_spaces(client: httpx.AsyncClient):
    """Test choice with multiple options and options containing spaces."""
    route = respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "choice_q": {
                    "type": "choice",
                    "choice": "very positive",
                    "confidence": 0.91,
                    "probabilities": {
                        "very positive": 0.91,
                        "positive": 0.05,
                        "neutral": 0.02,
                        "negative": 0.01,
                        "very negative": 0.01,
                    },
                }
            },
        },
    )

    response = await client.get(
        "/choice?input=I+love+this+product&choices=very+positive,positive,neutral,negative,very+negative"
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data["result"] == "very positive"
    assert data["confidence"] == 0.91
    assert "very positive" in data["probabilities"]

    # Verify criteria passed to Jev preserved the decoded spaces
    sent_payload = route.calls.last.request.read().decode()
    assert "very positive" in sent_payload
    assert "very negative" in sent_payload


@pytest.mark.asyncio
@respx.mock
async def test_url_encoding(client: httpx.AsyncClient):
    """Test that URL-encoded characters in input and choices are decoded properly."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=200,
        json={
            "model": "jev-latest",
            "answers": {
                "choice_q": {
                    "type": "choice",
                    "choice": "high priority",
                    "confidence": 0.85,
                    "probabilities": {"high priority": 0.85, "low priority": 0.15},
                }
            },
        },
    )

    response = await client.get(
        "/choice?input=Help%21%20Payment%20failed%20%26%20urgent&choices=high%20priority%2Clow%20priority"
    )
    assert response.status_code == 200
    assert response.json()["result"] == "high priority"


@pytest.mark.asyncio
async def test_missing_input(client: httpx.AsyncClient):
    """Test error when input query parameter is missing."""
    response = await client.get("/choice?choices=spam,not+spam")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "input is required"}


@pytest.mark.asyncio
async def test_missing_choices(client: httpx.AsyncClient):
    """Test error when choices query parameter is missing."""
    response = await client.get("/choice?input=Hello")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "choices is required"}


@pytest.mark.asyncio
async def test_empty_choices(client: httpx.AsyncClient):
    """Test error when choices query parameter is empty string."""
    response = await client.get("/choice?input=Hello&choices=")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "choices is required"}


@pytest.mark.asyncio
async def test_malformed_choices_too_few(client: httpx.AsyncClient):
    """Test error when fewer than 2 valid choices are provided."""
    response = await client.get("/choice?input=Hello&choices=onlyone")
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "At least 2 choices are required"}

    # With commas but only one non-empty choice
    response2 = await client.get("/choice?input=Hello&choices=onlyone,")
    assert response2.status_code == 400
    assert response2.json() == {"error": "At least 2 choices are required"}


@pytest.mark.asyncio
@respx.mock
async def test_upstream_jev_error(client: httpx.AsyncClient):
    """Test handling when TypeSafe Jev returns an upstream failure."""
    respx.post("https://api.typesafe.ai/v1/systemone").respond(
        status_code=500,
        json={"error": "Internal Jev inference error"},
    )

    response = await client.get("/choice?input=Hello&choices=a,b")
    assert response.status_code == 502
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert "error" in data
    assert "Jev" in data["error"]


@pytest.mark.asyncio
@respx.mock
async def test_upstream_timeout(client: httpx.AsyncClient):
    """Test handling when TypeSafe Jev times out."""
    respx.post("https://api.typesafe.ai/v1/systemone").mock(
        side_effect=httpx.TimeoutException("Connection timed out")
    )

    response = await client.get("/choice?input=Hello&choices=a,b")
    assert response.status_code == 504
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": "TypeSafe API request timed out"}

