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
You are RootCause AI.

Analyze the provided application error and return a JSON diagnosis.

Use repository context when provided.
Do not invent infrastructure that is not supported by the evidence.
Repository evidence is stronger than generic assumptions.

Preserve exact IP addresses, ports, hostnames, and service names.

If deterministic diagnostic evidence is provided:

- Treat exact runtime hosts, ports, configured hosts, configured ports,
  and boolean comparison results as authoritative.
- Do not change or rewrite exact IP addresses, hostnames, ports,
  service names, or boolean values.
- Prefer the narrowest root cause directly supported by the evidence.
- If hostname_mismatch is true, identify the hostname/configuration
  mismatch as the primary root cause.
- Do not claim that a service is stopped, crashed, or unavailable unless
  the provided evidence explicitly proves it.
- Possible causes that are not proven should be described as possibilities
  in the explanation, recommended fixes, or verification steps.
- Separate confirmed evidence from likely interpretations.

Error:
{error_text}

{context_section}

Return JSON only with exactly these fields:
{{
    "root_cause": "string",
    "confidence": 0.0,
    "explanation": "string",
    "evidence": ["string"],
    "recommended_fixes": ["string"],
    "verification_steps": ["string"]
}}
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