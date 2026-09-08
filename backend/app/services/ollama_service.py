import json

import httpx

from app.services.exceptions import (
    OllamaUnavailableError,
    OllamaTimeoutError,
    OllamaInvalidResponseError,
)


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"


async def analyze_with_ollama(error_text: str) -> dict:
    prompt = f"""
You are RootCause AI, a software debugging assistant.

Analyze the following error, logs, or stack trace:

{error_text}

Return ONLY valid JSON in exactly this structure:

{{
  "root_cause": "short root cause",
  "confidence": 0.0,
  "explanation": "clear technical explanation",
  "evidence": [
    "evidence from the provided error"
  ],
  "recommended_fixes": [
    "fix 1",
    "fix 2"
  ],
  "verification_steps": [
    "step 1",
    "step 2"
  ]
}}

Rules:
- confidence must be between 0 and 1
- return JSON only
- do not use markdown
- do not add text outside the JSON
- do not invent evidence
- if uncertain, lower the confidence score
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "think": False,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json=payload,
            )

            response.raise_for_status()

    except httpx.ConnectError as exc:
        raise OllamaUnavailableError(
            "Could not connect to Ollama"
        ) from exc

    except httpx.TimeoutException as exc:
        raise OllamaTimeoutError(
            "Ollama took too long to respond"
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise OllamaUnavailableError(
            f"Ollama returned HTTP {exc.response.status_code}"
        ) from exc

    data = response.json()

    model_output = data.get("response", "").strip()

    if not model_output:
        raise OllamaInvalidResponseError(
            "Ollama returned an empty response"
        )

    try:
        return json.loads(model_output)

    except json.JSONDecodeError as exc:
        raise OllamaInvalidResponseError(
            "Ollama returned invalid JSON"
        ) from exc