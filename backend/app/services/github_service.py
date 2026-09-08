from urllib.parse import urlparse

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