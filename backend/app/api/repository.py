from fastapi import APIRouter, HTTPException

from app.schemas import (
    RepositoryRequest,
    RepositoryMetadata,
    RepositoryTreeResponse,
    RepositoryTechnologyResponse,
)

from app.services.github_service import (
    get_repository_metadata,
    get_repository_tree,
    detect_important_files,
    get_file_content,
    InvalidGitHubUrlError,
    GitHubRepositoryNotFoundError,
)

from app.services.repository_analyzer import (
    analyze_file,
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
    request: RepositoryRequest,
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
        print("REPOSITORY METADATA ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        raise HTTPException(
            status_code=502,
            detail=f"Failed to communicate with GitHub: {str(exc)}",
        ) from exc


@router.post(
    "/tree",
    response_model=RepositoryTreeResponse,
)
async def repository_tree(
    request: RepositoryRequest,
):
    try:
        repository_url = str(
            request.repository_url
        )

        tree = await get_repository_tree(
            repository_url
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
        print("REPOSITORY TREE ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        raise HTTPException(
            status_code=502,
            detail=(
                f"Failed to retrieve repository tree: "
                f"{str(exc)}"
            ),
        ) from exc


@router.post(
    "/technologies",
    response_model=RepositoryTechnologyResponse,
)
async def repository_technologies(
    request: RepositoryRequest,
):
    try:
        repository_url = str(
            request.repository_url
        )

        print("STEP 1: Getting repository tree")

        tree = await get_repository_tree(
            repository_url
        )

        print("STEP 2: Repository tree retrieved")

        important_files = detect_important_files(
            tree
        )

        print("IMPORTANT FILES:")
        print(important_files)

        technologies = set()

        for file_path in important_files:

            print(f"FETCHING FILE: {file_path}")

            content = await get_file_content(
                repository_url,
                file_path,
            )

            print(
                f"FETCHED: {file_path} "
                f"({len(content)} characters)"
            )

            detected = analyze_file(
                file_path,
                content,
            )

            print(
                f"DETECTED FROM {file_path}: "
                f"{detected}"
            )

            technologies.update(detected)

        return RepositoryTechnologyResponse(
            important_files=important_files,
            technologies=sorted(
                technologies
            ),
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
        print("REPOSITORY ANALYSIS ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        raise HTTPException(
            status_code=502,
            detail=(
                f"Failed to analyze repository: "
                f"{str(exc)}"
            ),
        ) from exc