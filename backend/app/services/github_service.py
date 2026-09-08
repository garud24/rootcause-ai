from urllib.parse import urlparse
import base64
import httpx


GITHUB_API_BASE = "https://api.github.com"


class InvalidGitHubUrlError(Exception):
    pass


class GitHubRepositoryNotFoundError(Exception):
    pass


def parse_github_url(repository_url: str) -> tuple[str, str]:
    parsed = urlparse(repository_url)

    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise InvalidGitHubUrlError(
            "Only github.com repository URLs are supported"
        )

    parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if len(parts) < 2:
        raise InvalidGitHubUrlError(
            "GitHub URL must contain owner and repository name"
        )

    owner = parts[0]
    repo = parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo


async def get_repository_metadata(
    repository_url: str
) -> dict:

    owner, repo = parse_github_url(repository_url)

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 404:
        raise GitHubRepositoryNotFoundError(
            "GitHub repository was not found"
        )

    response.raise_for_status()

    data = response.json()

    return {
        "owner": owner,
        "repository": repo,
        "default_branch": data["default_branch"],
        "language": data.get("language"),
        "private": data["private"],
        "html_url": data["html_url"],
    }


async def get_repository_tree(
    repository_url: str
) -> list[dict]:

    owner, repo = parse_github_url(repository_url)

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RootCause-AI",
    }

    metadata_url = (
        f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    )

    async with httpx.AsyncClient(timeout=20.0) as client:

        metadata_response = await client.get(
            metadata_url,
            headers=headers,
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
            f"{default_branch}"
        )

        tree_response = await client.get(
            tree_url,
            params={
                "recursive": "1"
            },
            headers=headers,
        )

        if tree_response.status_code != 200:
            raise RuntimeError(
                f"GitHub tree API returned "
                f"{tree_response.status_code}: "
                f"{tree_response.text}"
            )

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

    "compose.yml",
    "compose.yaml",
    "compose.override.yml",
    "compose.override.yaml",
    "compose.deploy.yml",
    "compose.deploy.yaml",

    "Dockerfile",
    ".env.example",
    "application.yml",
    "application.yaml",
    "application.properties",
}


def detect_important_files(
    tree: list[dict]
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

async def get_file_content(
    repository_url: str,
    file_path: str,
) -> str:
    owner, repo = parse_github_url(repository_url)

    url = (
        f"{GITHUB_API_BASE}/repos/"
        f"{owner}/{repo}/contents/{file_path}"
    )

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            url,
            headers={
                "Accept": "application/vnd.github+json"
            },
        )

    if response.status_code == 404:
        raise GitHubRepositoryNotFoundError(
            f"File not found: {file_path}"
        )

    response.raise_for_status()

    data = response.json()

    encoded_content = data.get("content")

    if not encoded_content:
        return ""

    decoded = base64.b64decode(encoded_content)

    return decoded.decode(
        "utf-8",
        errors="ignore",
    )