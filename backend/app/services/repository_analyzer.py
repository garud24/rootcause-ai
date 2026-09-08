import json
import re


def analyze_package_json(content: str) -> list[str]:
    technologies = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return technologies

    dependencies = {}

    dependencies.update(
        data.get("dependencies", {})
    )

    dependencies.update(
        data.get("devDependencies", {})
    )

    mapping = {
        "react": "React",
        "next": "Next.js",
        "express": "Express",
        "fastify": "Fastify",
        "axios": "Axios",
        "pg": "PostgreSQL",
        "mongoose": "MongoDB",
        "redis": "Redis",
    }

    for package_name, technology in mapping.items():
        if package_name in dependencies:
            technologies.append(technology)

    return technologies


def analyze_requirements_txt(
    content: str,
) -> list[str]:

    technologies = []

    lines = content.splitlines()

    mapping = {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "sqlalchemy": "SQLAlchemy",
        "psycopg": "PostgreSQL",
        "psycopg2": "PostgreSQL",
        "redis": "Redis",
        "pymongo": "MongoDB",
        "httpx": "HTTP Client",
    }

    for line in lines:
        package = re.split(
            r"[=<>!~]",
            line.strip(),
        )[0].lower()

        if package in mapping:
            technologies.append(
                mapping[package]
            )

    return technologies


def analyze_file(
    file_path: str,
    content: str,
) -> list[str]:

    filename = file_path.split("/")[-1]

    if filename == "package.json":
        return analyze_package_json(
            content
        )

    if filename == "requirements.txt":
        return analyze_requirements_txt(
            content
        )

    return []
