import yaml


def analyze_docker_compose(content: str) -> dict:
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError:
        return {
            "nodes": [],
            "edges": [],
        }

    services = data.get("services", {})

    nodes = []
    edges = []

    for service_name, service_config in services.items():

        image = service_config.get("image", "")
        build = service_config.get("build")

        technology = detect_service_technology(
            service_name=service_name,
            image=image,
            build=build,
        )

        nodes.append({
            "id": service_name,
            "type": detect_node_type(
                service_name,
                technology,
            ),
            "technology": technology,
        })

        depends_on = service_config.get(
            "depends_on",
            []
        )

        if isinstance(depends_on, dict):
            dependencies = list(
                depends_on.keys()
            )
        else:
            dependencies = depends_on

        for dependency in dependencies:
            edges.append({
                "source": service_name,
                "target": dependency,
                "type": "depends_on",
            })

    return {
        "nodes": nodes,
        "edges": edges,
    }


def detect_service_technology(
    service_name: str,
    image: str,
    build,
) -> str:

    text = (
        f"{service_name} "
        f"{image}"
    ).lower()

    if "postgres" in text:
        return "PostgreSQL"

    if "redis" in text:
        return "Redis"

    if "mysql" in text:
        return "MySQL"

    if "mongo" in text:
        return "MongoDB"

    if "nginx" in text:
        return "Nginx"

    if "frontend" in service_name.lower():
        return "Frontend"

    if "backend" in service_name.lower():
        return "Backend"

    if build:
        return "Application Service"

    return "Unknown"


def detect_node_type(
    service_name: str,
    technology: str,
) -> str:

    if technology in {
        "PostgreSQL",
        "MySQL",
        "MongoDB",
    }:
        return "database"

    if technology == "Redis":
        return "cache"

    if technology == "Frontend":
        return "frontend"

    if technology == "Nginx":
        return "gateway"

    return "service"