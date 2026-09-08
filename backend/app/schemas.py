from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    error_text: str = Field(
        ...,
        min_length=3,
        max_length=20_000,
        description="Error message, stack trace, or logs"
    )


class AnalyzeResponse(BaseModel):
    root_cause: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    explanation: str

    evidence: list[str]

    recommended_fixes: list[str]

    verification_steps: list[str]