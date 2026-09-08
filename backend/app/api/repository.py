from fastapi import APIRouter, HTTPException

from app.schemas import (
    RepositoryRequest,
    RepositoryMetadata,
    RepositoryTreeResponse,
    RepositoryTechnologyResponse,
    RepositoryGraphResponse,
    GraphDiagnosisRequest,
    GraphDiagnosisResponse,
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

from app.services.graph_builder import (
    build_graph,
)

from app.services.docker_compose_analyzer import (
    analyze_docker_compose,
)

from app.services.error_graph_matcher import (
    match_error_to_graph,
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

@router.post(
    "/graph",
    response_model=RepositoryGraphResponse,
)
async def repository_graph(
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

        technologies = set()

        compose_graph = {
            "nodes": [],
            "edges": [],
        }

        for file_path in important_files:

            content = await get_file_content(
                repository_url,
                file_path,
            )

            detected = analyze_file(
                file_path,
                content,
            )

            technologies.update(detected)

            filename = file_path.split("/")[-1]

            if filename in {
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml",
                "compose.override.yml",
                "compose.override.yaml",
                "compose.deploy.yml",
                "compose.deploy.yaml",
            }:
                parsed_compose = analyze_docker_compose(
                    content
                )

                compose_graph["nodes"].extend(
                    parsed_compose["nodes"]
                )

                compose_graph["edges"].extend(
                    parsed_compose["edges"]
                )

        unique_nodes = {}

        for node in compose_graph["nodes"]:
            unique_nodes[node["id"]] = node

        unique_edges = {}

        for edge in compose_graph["edges"]:
            key = (
                edge["source"],
                edge["target"],
                edge["type"],
            )

            unique_edges[key] = edge

        compose_graph = {
            "nodes": list(
                unique_nodes.values()
            ),
            "edges": list(
                unique_edges.values()
            ),
        }

        graph = build_graph(
            sorted(technologies),
            compose_graph,
        )

        return RepositoryGraphResponse(
            **graph
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
        print("GRAPH BUILD ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        raise HTTPException(
            status_code=502,
            detail=f"Failed to build repository graph: {str(exc)}",
        ) from exc

@router.post(
    "/diagnose",
    response_model=GraphDiagnosisResponse,
)
async def diagnose_repository_error(
    request: GraphDiagnosisRequest,
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

        technologies = set()

        compose_graph = {
            "nodes": [],
            "edges": [],
        }

        for file_path in important_files:

            content = await get_file_content(
                repository_url,
                file_path,
            )

            detected = analyze_file(
                file_path,
                content,
            )

            technologies.update(detected)

            filename = file_path.split("/")[-1]

            if filename in {
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml",
                "compose.override.yml",
                "compose.override.yaml",
                "compose.deploy.yml",
                "compose.deploy.yaml",
            }:
                parsed_compose = (
                    analyze_docker_compose(
                        content
                    )
                )

                compose_graph["nodes"].extend(
                    parsed_compose["nodes"]
                )

                compose_graph["edges"].extend(
                    parsed_compose["edges"]
                )

        unique_nodes = {}

        for node in compose_graph["nodes"]:
            unique_nodes[node["id"]] = node

        unique_edges = {}

        for edge in compose_graph["edges"]:
            key = (
                edge["source"],
                edge["target"],
                edge["type"],
            )

            unique_edges[key] = edge

        compose_graph = {
            "nodes": list(
                unique_nodes.values()
            ),
            "edges": list(
                unique_edges.values()
            ),
        }

        graph = build_graph(
            sorted(technologies),
            compose_graph,
        )

        diagnosis = match_error_to_graph(
            request.error_text,
            graph,
        )

        return GraphDiagnosisResponse(
            **diagnosis
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
        print("GRAPH DIAGNOSIS ERROR:")
        print(type(exc).__name__)
        print(str(exc))

        raise HTTPException(
            status_code=502,
            detail=(
                f"Failed to diagnose repository: "
                f"{str(exc)}"
            ),
        ) from exc        