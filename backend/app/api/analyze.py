from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.ollama_service import analyze_with_ollama
from app.services.exceptions import (
    OllamaUnavailableError,
    OllamaTimeoutError,
    OllamaInvalidResponseError,
)


router = APIRouter(
    prefix="/api",
    tags=["analysis"],
)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_error(request: AnalyzeRequest):
    try:
        result = await analyze_with_ollama(
            request.error_text
        )

        return AnalyzeResponse(**result)

    except OllamaUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except OllamaTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=str(exc),
        )

    except OllamaInvalidResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM response did not match the expected schema",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error",
        ) from exc