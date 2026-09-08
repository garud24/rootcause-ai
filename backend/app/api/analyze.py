from fastapi import APIRouter, HTTPException

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.ollama_service import analyze_with_ollama


router = APIRouter(
    prefix="/api",
    tags=["analysis"]
)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_error(request: AnalyzeRequest):
    try:
        result = await analyze_with_ollama(
            request.error_text
        )

        return AnalyzeResponse(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}"
        )