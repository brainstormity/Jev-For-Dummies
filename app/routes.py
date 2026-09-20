"""FastAPI route definitions for JEV for Dummies."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from app.typesafe import evaluate_choice, evaluate_noul, evaluate_score

router = APIRouter()


@router.get("/health", summary="Health check", tags=["System"])
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@router.get("/choice", summary="Choice decision", tags=["Primitives"])
async def choice_endpoint(
    input: Optional[str] = Query(
        None,
        description="The content to evaluate",
        examples=["Win a free brand new car! Click here now."],
    ),
    choices: Optional[str] = Query(
        None,
        description="Comma-separated options to select from",
        examples=["scam,not scam"],
    ),
) -> Response:
    """Evaluate an input against a comma-separated list of choices."""
    if input is None or not input.strip():
        return JSONResponse(status_code=400, content={"error": "input is required"})

    if choices is None or not choices.strip():
        return JSONResponse(status_code=400, content={"error": "choices is required"})

    # Parse comma-separated choices
    raw_list = [c.strip() for c in choices.split(",")]
    parsed_choices = [c for c in raw_list if c]

    if len(parsed_choices) < 2:
        return JSONResponse(status_code=400, content={"error": "At least 2 choices are required"})

    res = await evaluate_choice(input.strip(), parsed_choices)
    return JSONResponse(status_code=200, content=res)


@router.get("/noul", summary="Noul yes/no decision", tags=["Primitives"])
async def noul_endpoint(
    input: Optional[str] = Query(
        None,
        description="The content to evaluate",
        examples=["Win a free brand new car! Click here now."],
    ),
    question: Optional[str] = Query(
        None,
        description="The yes/no question to evaluate",
        examples=["Is this a scam?"],
    ),
) -> Response:
    """Evaluate an input against a yes/no question."""
    if input is None or not input.strip():
        return JSONResponse(status_code=400, content={"error": "input is required"})

    if question is None or not question.strip():
        return JSONResponse(status_code=400, content={"error": "question is required"})

    res = await evaluate_noul(input.strip(), question.strip())
    return JSONResponse(status_code=200, content=res)


@router.get("/score", summary="Score rating", tags=["Primitives"])
async def score_endpoint(
    input: Optional[str] = Query(
        None,
        description="The content to evaluate",
        examples=["This user is extremely toxic"],
    ),
    question: Optional[str] = Query(
        None,
        description="The rating question",
        examples=["How toxic is this?"],
    ),
    min: Optional[str] = Query(
        None,
        description="Minimum score (integer)",
        examples=["0"],
    ),
    max: Optional[str] = Query(
        None,
        description="Maximum score (integer)",
        examples=["10"],
    ),
) -> Response:
    """Evaluate an input rating along a min-to-max numeric scale."""
    if input is None or not input.strip():
        return JSONResponse(status_code=400, content={"error": "input is required"})

    if question is None or not question.strip():
        return JSONResponse(status_code=400, content={"error": "question is required"})

    if min is None or not str(min).strip():
        return JSONResponse(status_code=400, content={"error": "min is required"})

    if max is None or not str(max).strip():
        return JSONResponse(status_code=400, content={"error": "max is required"})

    try:
        min_val = int(min)
    except (ValueError, TypeError):
        return JSONResponse(status_code=400, content={"error": "min must be an integer"})

    try:
        max_val = int(max)
    except (ValueError, TypeError):
        return JSONResponse(status_code=400, content={"error": "max must be an integer"})

    if max_val <= min_val:
        return JSONResponse(status_code=400, content={"error": "max must be greater than min"})

    res = await evaluate_score(input.strip(), question.strip(), min_val, max_val)
    return JSONResponse(status_code=200, content=res)
