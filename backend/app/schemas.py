from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    error_text: str = Field(
        ...,
        min_length=3,
        max_length=20_000,
        description="Error message, stack trace, or logs"
    )
    repository_url: HttpUrl | None = Field(
        default=None,
        description="Optional GitHub repository URL"
    )


class AnalyzeResponse(BaseModel):
    root_cause: str

    confidence: float = Field(ge=0.0, le=1.0)

    explanation: str

    evidence: list[str]

    recommended_fixes: list[str]

    verification_steps: list[str]

class RepositoryRequest(BaseModel):
    repository_url: HttpUrl


class RepositoryMetadata(BaseModel):
    owner: str
    repository: str
    default_branch: str
    language: str | None
    private: bool
    html_url: str

class RepositoryTreeResponse(BaseModel):
    total_files: int
    important_files: list[str] 

class RepositoryTechnologyResponse(BaseModel):
    important_files: list[str]
    technologies: list[str]           