import re


PORT_TECHNOLOGY_MAP = {
    5432: "PostgreSQL",
    3306: "MySQL",
    6379: "Redis",
    27017: "MongoDB",
    9200: "Elasticsearch",
    5672: "RabbitMQ",
}


def extract_ports(error_text: str) -> list[int]:
    matches = re.findall(
        r":(\d{2,5})",
        error_text,
    )

    return [
        int(port)
        for port in matches
    ]


def match_error_to_graph(
    error_text: str,
    graph: dict,
) -> dict:

    ports = extract_ports(
        error_text
    )

    candidates = []

    for port in ports:

        expected_technology = (
            PORT_TECHNOLOGY_MAP.get(port)
        )

        if not expected_technology:
            continue

        for node in graph.get("nodes", []):

            if (
                node.get("technology")
                == expected_technology
            ):
                candidates.append({
                    "node_id": node["id"],
                    "technology": expected_technology,
                    "reason": (
                        f"Error references port {port}, "
                        f"commonly used by "
                        f"{expected_technology}"
                    ),
                    "confidence": 0.95,
                })

    if candidates:
        best_match = candidates[0]

        return {
            "matched": True,
            "affected_node": best_match["node_id"],
            "technology": best_match["technology"],
            "confidence": best_match["confidence"],
            "reason": best_match["reason"],
        }

    return {
        "matched": False,
        "affected_node": None,
        "technology": None,
        "confidence": 0.0,
        "reason": (
            "No deterministic graph match "
            "was found"
        ),
    }