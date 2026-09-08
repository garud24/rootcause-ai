from fastapi import APIRouter, HTTPException

from app.schemas import (
    RepositoryRequest,
    RepositoryMetadata,
)

from app.services.github_service import (
    get_repository_metadata,
    InvalidGitHubUrlError,
    GitHubRepositoryNotFoundError,
)


router = APIRouter(
    prefix="/api/repository",
    tags=["repository"],
)


@router.post(
    "/metadata",
    response_model=RepositoryMetadata,
)
async def repository_metadata(
    request: RepositoryRequest
):
    try:
        result = await get_repository_metadata(
            str(request.repository_url)
        )

        return RepositoryMetadata(**result)

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

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to communicate with GitHub",
        ) from exc