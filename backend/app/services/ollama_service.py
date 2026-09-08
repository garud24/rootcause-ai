import json

import httpx

from app.services.exceptions import (
    OllamaUnavailableError,
    OllamaTimeoutError,
    OllamaInvalidResponseError,
)


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"


async def analyze_with_ollama(
    error_text: str,
    repository_context: str | None = None,
) -> dict:
    context_section = ""

    if repository_context:
        context_section = f"""
    Repository context:
    {repository_context}
"""
    prompt = f"""
You are RootCause AI, a software debugging assistant.

Analyze the following application error.

Error:
{error_text}

{context_section}

Return ONLY valid JSON with exactly these fields:

{{
  "root_cause": "string",
  "confidence": 0.0,
  "explanation": "string",
  "evidence": ["string"],
  "recommended_fixes": ["string"],
  "verification_steps": ["string"]
}}

Rules:

1. Use the repository context when it is provided.
2. Do not invent infrastructure that is not supported by the context.
3. Treat the repository context as stronger evidence than generic assumptions.
4. Preserve exact technical values from the error such as:
   - IP addresses
   - ports
   - hostnames
   - service names
5. If the repository contains a Docker Compose service, prefer repository-specific
   fixes over generic operating-system service commands.
6. Clearly distinguish between:
   - confirmed evidence
   - likely interpretation
7. If evidence is insufficient, lower confidence rather than guessing.
8. Do not include markdown.
9. Return JSON only.
10. If repository configuration shows a service hostname that differs from the
hostname in the runtime error, explicitly identify this as a possible
configuration mismatch.
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