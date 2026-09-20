"""Main FastAPI application for JEV for Dummies."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import router
from app.typesafe import (
    TypeSafeConfigError,
    TypeSafeUpstreamError,
    close_http_client,
)

# Load environment variables from .env if present
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for setup and teardown."""
    yield
    # Clean up persistent HTTP client
    await close_http_client()


app = FastAPI(
    title="JEV for Dummies",
    description=(
        "A tiny, open-source, self-hosted HTTP API wrapper around TypeSafe's Jev. "
        "Turns Jev's decision primitives into simple HTTP GET requests."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.exception_handler(TypeSafeConfigError)
async def config_error_handler(request: Request, exc: TypeSafeConfigError) -> JSONResponse:
    """Handle missing configuration errors."""
    return JSONResponse(
        status_code=500,
        content={"error": exc.message},
    )


@app.exception_handler(TypeSafeUpstreamError)
async def upstream_error_handler(request: Request, exc: TypeSafeUpstreamError) -> JSONResponse:
    """Handle TypeSafe API upstream failures."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle general value validation errors."""
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors and format into standard error JSON."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = first.get("loc", [])
        field = loc[-1] if loc else "parameter"
        msg = f"{field} is required" if first.get("type") == "missing" else first.get("msg", "Invalid parameter")
        return JSONResponse(status_code=400, content={"error": msg})
    return JSONResponse(status_code=400, content={"error": "Invalid request parameters"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions such as 404 Not Found."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors without leaking stack traces."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Register endpoints
app.include_router(router)
