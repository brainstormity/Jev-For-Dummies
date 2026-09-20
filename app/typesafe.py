"""TypeSafe Jev API adapter.

Handles communication with TypeSafe's System One raw HTTP API.
Does not depend on any third-party SDK.
"""

from __future__ import annotations

import os
from typing import Any, Optional
import httpx


class TypeSafeConfigError(Exception):
    """Raised when TypeSafe configuration (such as API key) is missing."""

    def __init__(self, message: str = "TypeSafe API key is not configured"):
        super().__init__(message)
        self.message = message


class TypeSafeUpstreamError(Exception):
    """Raised when an upstream call to TypeSafe Jev fails."""

    def __init__(self, message: str = "Jev request failed", status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# Global persistent client for connection reuse
_http_client: Optional[httpx.AsyncClient] = None


def get_api_key() -> str:
    """Retrieve the TypeSafe API key from environment."""
    key = os.getenv("TYPESAFE_API_KEY", "").strip()
    if not key:
        raise TypeSafeConfigError("TypeSafe API key is not configured")
    return key


def get_base_url() -> str:
    """Retrieve the TypeSafe API base URL."""
    return os.getenv("TYPESAFE_BASE_URL", "https://api.typesafe.ai").rstrip("/")


def get_model() -> str:
    """Retrieve the model name to use."""
    return os.getenv("TYPESAFE_MODEL", "jev-latest").strip()


def get_timeout() -> float:
    """Retrieve the default HTTP timeout."""
    try:
        return float(os.getenv("TYPESAFE_TIMEOUT", "15.0"))
    except ValueError:
        return 15.0


async def get_http_client() -> httpx.AsyncClient:
    """Get or initialize the shared async HTTP client."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=get_timeout())
    return _http_client


async def close_http_client() -> None:
    """Close the shared async HTTP client."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


async def call_systemone(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute a raw POST request to TypeSafe's System One API endpoint.

    Args:
        payload: SystemOne evaluation request dictionary.

    Returns:
        JSON response dictionary from TypeSafe.

    Raises:
        TypeSafeConfigError: If TYPESAFE_API_KEY is missing.
        TypeSafeUpstreamError: If the upstream request fails.
    """
    api_key = get_api_key()
    base_url = get_base_url()
    url = f"{base_url}/v1/systemone"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    client = await get_http_client()

    try:
        response = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException:
        raise TypeSafeUpstreamError("TypeSafe API request timed out", status_code=504)
    except httpx.RequestError as exc:
        raise TypeSafeUpstreamError(f"Failed to connect to TypeSafe API: {exc.__class__.__name__}", status_code=502)

    if response.status_code != 200:
        # Check for upstream message without leaking secrets
        upstream_msg = "Jev request failed"
        try:
            body = response.json()
            if isinstance(body, dict):
                detail = body.get("message") or body.get("error")
                if detail and isinstance(detail, str):
                    upstream_msg = f"Jev request failed: {detail}"
        except Exception:
            pass

        status = response.status_code
        if status in (401, 403):
            # Do not leak key validity in detail
            raise TypeSafeUpstreamError("Jev authentication failed", status_code=status)
        elif status == 429:
            raise TypeSafeUpstreamError("Jev rate limit exceeded", status_code=429)
        elif status >= 500:
            raise TypeSafeUpstreamError("Jev upstream service error", status_code=502)
        else:
            raise TypeSafeUpstreamError(upstream_msg, status_code=status)

    try:
        data = response.json()
    except Exception:
        raise TypeSafeUpstreamError("Invalid JSON received from Jev API", status_code=502)

    return data


async def evaluate_choice(input_text: str, choices: list[str]) -> dict[str, Any]:
    """Execute a Jev Choice evaluation.

    Args:
        input_text: The state string to evaluate.
        choices: List of choice strings.

    Returns:
        Dictionary containing 'result' and available metadata (confidence, probabilities).
    """
    payload = {
        "state": input_text,
        "model": get_model(),
        "questions": {
            "choice_q": {
                "type": "choice",
                "instructions": "Select the option that best matches the input.",
                "criteria": {c: None for c in choices},
            }
        },
    }

    raw = await call_systemone(payload)

    answers = raw.get("answers", {})
    ans = answers.get("choice_q")
    if not ans or not isinstance(ans, dict):
        raise TypeSafeUpstreamError("Missing choice answer in Jev response", status_code=502)

    normalized: dict[str, Any] = {
        "result": ans.get("choice"),
    }

    if "confidence" in ans and ans["confidence"] is not None:
        normalized["confidence"] = ans["confidence"]

    if "probabilities" in ans and isinstance(ans["probabilities"], dict):
        normalized["probabilities"] = ans["probabilities"]

    return normalized


async def evaluate_noul(input_text: str, question: str) -> dict[str, Any]:
    """Execute a Jev Noul (yes/no) evaluation.

    Args:
        input_text: The state string to evaluate.
        question: The yes/no question or proposition.

    Returns:
        Dictionary containing 'result' (bool) and available metadata.
    """
    payload = {
        "state": input_text,
        "model": get_model(),
        "questions": {
            "noul_q": {
                "type": "noul",
                "instructions": question,
            }
        },
    }

    raw = await call_systemone(payload)

    answers = raw.get("answers", {})
    ans = answers.get("noul_q")
    if not ans or not isinstance(ans, dict):
        raise TypeSafeUpstreamError("Missing noul answer in Jev response", status_code=502)

    noul_val = ans.get("noul")
    if noul_val is None or not isinstance(noul_val, (int, float)):
        raise TypeSafeUpstreamError("Invalid noul value in Jev response", status_code=502)

    # Boolean result: probability >= 0.5 is True
    normalized: dict[str, Any] = {
        "result": bool(noul_val >= 0.5),
    }

    # Preserve any confidence or probability information if returned by Jev
    if "confidence" in ans and ans["confidence"] is not None:
        normalized["confidence"] = ans["confidence"]
    elif "probability" in ans and ans["probability"] is not None:
        normalized["probability"] = ans["probability"]

    return normalized


async def evaluate_score(input_text: str, question: str, min_val: int, max_val: int) -> dict[str, Any]:
    """Execute a Jev Score evaluation on a scale from min_val to max_val.

    Args:
        input_text: The state string to evaluate.
        question: The rating question.
        min_val: Minimum integer score.
        max_val: Maximum integer score.

    Returns:
        Dictionary containing 'result' (int) and available metadata (confidence, probabilities).
    """
    if max_val <= min_val:
        raise ValueError("max must be greater than min")

    steps = max_val - min_val + 1
    # Jev allows between 2 and 10 levels in criteria
    if steps <= 10:
        num_levels = steps
        criteria = [str(min_val + i) for i in range(steps)]
    else:
        num_levels = 10
        criteria = [
            str(round(min_val + i * (max_val - min_val) / (num_levels - 1)))
            for i in range(num_levels)
        ]

    payload = {
        "state": input_text,
        "model": get_model(),
        "questions": {
            "score_q": {
                "type": "score",
                "instructions": question,
                "criteria": criteria,
            }
        },
    }

    raw = await call_systemone(payload)

    answers = raw.get("answers", {})
    ans = answers.get("score_q")
    if not ans or not isinstance(ans, dict):
        raise TypeSafeUpstreamError("Missing score answer in Jev response", status_code=502)

    raw_score = ans.get("score")
    if raw_score is None or not isinstance(raw_score, (int, float)):
        raise TypeSafeUpstreamError("Invalid score in Jev response", status_code=502)

    # Convert Jev level position (0 to num_levels - 1) back to user scale min..max
    normalized_pos = raw_score / (num_levels - 1) if num_levels > 1 else 0.0
    scaled_score = min_val + normalized_pos * (max_val - min_val)
    result_val = int(round(scaled_score))

    # Clamp result within [min_val, max_val]
    result_val = max(min_val, min(max_val, result_val))

    normalized: dict[str, Any] = {
        "result": result_val,
    }

    if "confidence" in ans and ans["confidence"] is not None:
        normalized["confidence"] = ans["confidence"]

    if "probabilities" in ans and isinstance(ans["probabilities"], dict):
        normalized["probabilities"] = ans["probabilities"]

    return normalized
