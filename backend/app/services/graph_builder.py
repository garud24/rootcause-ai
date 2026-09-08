def build_graph(
    technologies: list[str],
    compose_graph: dict | None = None,
) -> dict:

    nodes = []
    edges = []

    if compose_graph:
        nodes.extend(
            compose_graph.get("nodes", [])
        )

        edges.extend(
            compose_graph.get("edges", [])
        )

    existing_node_ids = {
        node["id"]
        for node in nodes
    }

    tech_set = set(technologies)

    if (
        "React" in tech_set
        and "frontend" not in existing_node_ids
    ):
        nodes.append({
            "id": "frontend",
            "type": "frontend",
            "technology": "React",
        })

    if (
        "FastAPI" in tech_set
        and "backend" not in existing_node_ids
    ):
        nodes.append({
            "id": "backend",
            "type": "service",
            "technology": "FastAPI",
        })

    if (
        "PostgreSQL" in tech_set
        and "database" not in existing_node_ids
        and "db" not in existing_node_ids
    ):
        nodes.append({
            "id": "database",
            "type": "database",
            "technology": "PostgreSQL",
        })

    return {
        "nodes": nodes,
        "edges": edges,
    }