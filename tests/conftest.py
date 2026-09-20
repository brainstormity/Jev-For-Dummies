"""Pytest configuration and shared fixtures for JEV for Dummies tests."""

import os
from typing import AsyncIterator
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport

# Ensure a mock API key is set for unit tests
os.environ["TYPESAFE_API_KEY"] = "mock-typesafe-api-key"
os.environ["TYPESAFE_BASE_URL"] = "https://api.typesafe.ai"

from app.main import app
from app.typesafe import close_http_client


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async test client connected to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await close_http_client()
