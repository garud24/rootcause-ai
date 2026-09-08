def build_graph(
    technologies: list[str],
) -> dict:

    nodes = []
    edges = []

    tech_set = set(technologies)

    if "React" in tech_set:
        nodes.append({
            "id": "frontend",
            "type": "frontend",
            "technology": "React",
        })

    if "Next.js" in tech_set:
        nodes.append({
            "id": "frontend",
            "type": "frontend",
            "technology": "Next.js",
        })

    if "FastAPI" in tech_set:
        nodes.append({
            "id": "backend",
            "type": "service",
            "technology": "FastAPI",
        })

    if "Express" in tech_set:
        nodes.append({
            "id": "backend",
            "type": "service",
            "technology": "Express",
        })

    if "PostgreSQL" in tech_set:
        nodes.append({
            "id": "database",
            "type": "database",
            "technology": "PostgreSQL",
        })

    if "Redis" in tech_set:
        nodes.append({
            "id": "cache",
            "type": "cache",
            "technology": "Redis",
        })

    node_ids = {
        node["id"]
        for node in nodes
    }

    if (
        "frontend" in node_ids
        and "backend" in node_ids
    ):
        edges.append({
            "source": "frontend",
            "target": "backend",
            "type": "http",
        })

    if (
        "backend" in node_ids
        and "database" in node_ids
    ):
        edges.append({
            "source": "backend",
            "target": "database",
            "type": "database",
        })

    if (
        "backend" in node_ids
        and "cache" in node_ids
    ):
        edges.append({
            "source": "backend",
            "target": "cache",
            "type": "cache",
        })

    return {
        "nodes": nodes,
        "edges": edges,
    }