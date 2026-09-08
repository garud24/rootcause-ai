import re
from urllib.parse import urlparse

def extract_compose_configuration(
    content: str,
) -> list[str]:

    evidence = []

    lines = content.splitlines()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        lowered = stripped.lower()

        if "database_url" in lowered:

            if ":" in stripped:
                _, value = stripped.split(
                    ":",
                    1,
                )

            elif "=" in stripped:
                _, value = stripped.split(
                    "=",
                    1,
                )

            else:
                continue

            value = value.strip().strip(
                "\"'"
            )

            evidence.extend(
                extract_database_url_evidence(
                    value
                )
            )

            continue

        if any(
            key in lowered
            for key in [
                "postgres_server",
                "postgres_host",
                "postgres_port",
                "db_host",
                "db_port",
            ]
        ):
            evidence.append(
                sanitize_config_line(
                    stripped
                )
            )

    return evidence


def sanitize_config_line(
    line: str,
) -> str:

    sensitive_keywords = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
    }

    lowered = line.lower()

    if any(
        keyword in lowered
        for keyword in sensitive_keywords
    ):
        key = re.split(
            r"[:=]",
            line,
            maxsplit=1,
        )[0]

        return f"{key}=<redacted>"

    return line

def extract_database_url_evidence(
    value: str,
) -> list[str]:

    evidence = []

    try:
        parsed = urlparse(value)

        if parsed.scheme:
            evidence.append(
                f"DATABASE_URL scheme={parsed.scheme}"
            )

        if parsed.hostname:
            evidence.append(
                f"DATABASE_URL host={parsed.hostname}"
            )

        if parsed.port:
            evidence.append(
                f"DATABASE_URL port={parsed.port}"
            )

    except ValueError:
        pass

    return evidence