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
- If the repository context says the backend depends on the affected
  database node, treat that as evidence that the backend and database
  are connected through the repository's application architecture.

- If the backend depends on the database and the runtime host is
  127.0.0.1 while the configured database host is a different hostname,
  do not automatically recommend changing the configured hostname to
  127.0.0.1.

- Instead, recommend checking whether the effective runtime configuration
  has incorrectly overridden the repository-configured database hostname.

- Do not assume 127.0.0.1 is the correct database hostname for a
  containerized backend unless the evidence explicitly proves that.
  
- Never claim that a host, port, service, or endpoint is reachable,
  running, healthy, or available unless the provided evidence explicitly
  proves it.

- A connection-refused error is evidence that the attempted connection
  was not accepted. Do not describe the attempted endpoint as reachable.

- Recommended verification steps may test whether a service is reachable,
  but must not assume that reachability has already been established.

- Copy exact runtime evidence verbatim from the provided error/context.
  Never alter IP addresses, hostnames, ports, or service names.

- Do not say a mismatch "caused" a failure unless the evidence directly
  establishes causality. Prefer wording such as "likely caused",
  "strongly suggests", or "is consistent with".

- When ECONNREFUSED is present, state only that the attempted endpoint
  refused the connection. Do not infer more than the evidence supports.

- Do not recommend making a Compose service hostname resolve to 127.0.0.1.
  Inside a container, 127.0.0.1 normally refers to that same container.

- If repository configuration uses a non-localhost database hostname and
  runtime evidence shows 127.0.0.1, prefer investigating why the runtime
  configuration differs from repository configuration.

- Do not recommend changing the database service to listen on 127.0.0.1
  unless the evidence explicitly shows the application and database run
  in the same network namespace or on the same host.

- Do not state that a mismatch caused the connection refusal unless
  causality is directly established. Prefer "likely", "suggests", or
  "is consistent with".

- Never infer the address a service is listening on from ECONNREFUSED.
  ECONNREFUSED only proves the attempted endpoint rejected the connection.

- Do not say a database is listening on 127.0.0.1 unless explicit evidence
  confirms that binding.

- When runtime_host differs from configured_host, describe the mismatch as
  confirmed, but describe the exact cause of the failed connection as likely
  unless directly proven.  

- A hostname or Compose service name is not the same as a database
  listening address. Do not say a service "listens on" a hostname
  unless explicit evidence supports that wording.

- A confirmed hostname mismatch may strongly suggest the failure source,
  but do not describe it as the direct cause of ECONNREFUSED unless
  causality is explicitly proven.        

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