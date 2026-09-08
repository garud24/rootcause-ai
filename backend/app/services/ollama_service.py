import json
import httpx


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"


async def analyze_with_ollama(error_text: str) -> dict:
    prompt = f"""
You are RootCause AI, a software debugging assistant.

Analyze the following error, logs, or stack trace:

{error_text}

Return ONLY valid JSON with exactly this structure:

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
- do not add explanations outside the JSON
- do not invent evidence
- if uncertain, lower the confidence score
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "think": False
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

    print("OLLAMA RAW RESPONSE:")
    print(data)

    model_output = data.get("response", "").strip()

    if not model_output:
        raise ValueError(
            "Ollama returned an empty response"
        )

    try:
        return json.loads(model_output)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON: {model_output}"
        ) from exc