from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
)

from app.services.diagnosis_service import (
    diagnose_repository,
)

from app.services.github_service import (
    InvalidGitHubUrlError,
    GitHubRepositoryNotFoundError,
)

from app.services.exceptions import (
    OllamaUnavailableError,
    OllamaTimeoutError,
    OllamaInvalidResponseError,
)


router = APIRouter(
    prefix="/api/analyze",
    tags=["analysis"],
)


@router.post(
    "/repository",
    response_model=RepositoryAnalysisResponse,
)
async def analyze_repository(
    request: RepositoryAnalysisRequest,
):

    try:

        result = await diagnose_repository(
            repository_url=str(
                request.repository_url
            ),
            error_text=request.error_text,
        )

        return RepositoryAnalysisResponse(
            **result
        )

    except InvalidGitHubUrlError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except GitHubRepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

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

    except Exception as exc:

        print(
            "REPOSITORY ANALYSIS ERROR:"
        )

        print(
            type(exc).__name__
        )

        print(
            str(exc)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Repository analysis failed: "
                f"{str(exc)}"
            ),
        ) from exc