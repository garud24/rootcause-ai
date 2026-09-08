from fastapi import APIRouter, HTTPException

from app.schemas import (
    RepositoryRequest,
    RepositoryMetadata,
    RepositoryTreeResponse,
)

from app.services.github_service import (
    get_repository_metadata,
    InvalidGitHubUrlError,
    GitHubRepositoryNotFoundError,
    get_repository_tree,
    detect_important_files,
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

async def get_repository_tree(
    repository_url: str,
) -> list[dict]:
    owner, repo = parse_github_url(repository_url)

    metadata_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        metadata_response = await client.get(
            metadata_url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

        if metadata_response.status_code == 404:
            raise GitHubRepositoryNotFoundError(
                "GitHub repository was not found"
            )

        metadata_response.raise_for_status()

        metadata = metadata_response.json()

        default_branch = metadata["default_branch"]

        tree_url = (
            f"{GITHUB_API_BASE}/repos/"
            f"{owner}/{repo}/git/trees/"
            f"{default_branch}?recursive=1"
        )

        tree_response = await client.get(
            tree_url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

        tree_response.raise_for_status()

    tree_data = tree_response.json()

    return tree_data.get("tree", [])

IMPORTANT_FILENAMES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
    ".env.example",
    "application.yml",
    "application.yaml",
    "application.properties",
}


def detect_important_files(
    tree: list[dict],
) -> list[str]:
    important_files = []

    for item in tree:
        if item.get("type") != "blob":
            continue

        path = item.get("path", "")

        filename = path.split("/")[-1]

        if filename in IMPORTANT_FILENAMES:
            important_files.append(path)

    return important_files 

@router.post(
    "/tree",
    response_model=RepositoryTreeResponse,
)
async def repository_tree(
    request: RepositoryRequest
):
    try:
        tree = await get_repository_tree(
            str(request.repository_url)
        )

        important_files = detect_important_files(
            tree
        )

        total_files = sum(
            1
            for item in tree
            if item.get("type") == "blob"
        )

        return RepositoryTreeResponse(
            total_files=total_files,
            important_files=important_files,
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

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve repository tree",
        ) from exc      