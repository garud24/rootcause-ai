import re


def extract_runtime_host_port(
    error_text: str,
) -> tuple[str | None, int | None]:

    match = re.search(
        r"((?:\d{1,3}\.){3}\d{1,3}):(\d{2,5})",
        error_text,
    )

    if not match:
        return None, None

    host = match.group(1)
    port = int(match.group(2))

    return host, port


def extract_configured_database_values(
    configuration_evidence: list[str],
) -> tuple[str | None, int | None]:

    configured_host = None
    configured_port = None

    for item in configuration_evidence:

        if item.startswith(
            "DATABASE_URL host="
        ):
            configured_host = item.split(
                "=",
                1,
            )[1]

        elif item.startswith(
            "DATABASE_URL port="
        ):
            value = item.split(
                "=",
                1,
            )[1]

            try:
                configured_port = int(value)
            except ValueError:
                pass

    return (
        configured_host,
        configured_port,
    )


def build_diagnostic_evidence(
    error_text: str,
    configuration_evidence: list[str],
    graph: dict,
    graph_diagnosis: dict,
) -> dict:

    runtime_host, runtime_port = (
        extract_runtime_host_port(
            error_text
        )
    )

    (
        configured_host,
        configured_port,
    ) = extract_configured_database_values(
        configuration_evidence
    )

    affected_node = graph_diagnosis.get(
        "affected_node"
    )

    affected_technology = (
        graph_diagnosis.get(
            "technology"
        )
    )

    hostname_mismatch = None

    if (
        runtime_host
        and configured_host
    ):
        hostname_mismatch = (
            runtime_host
            != configured_host
        )

    port_matches = None

    if (
        runtime_port is not None
        and configured_port is not None
    ):
        port_matches = (
            runtime_port
            == configured_port
        )

    relevant_edges = []

    if affected_node:

        for edge in graph.get(
            "edges",
            [],
        ):
            if (
                edge.get("source")
                == affected_node
                or edge.get("target")
                == affected_node
            ):
                relevant_edges.append(
                    edge
                )

    return {
        "runtime_host": runtime_host,
        "runtime_port": runtime_port,

        "configured_host": configured_host,
        "configured_port": configured_port,

        "affected_node": affected_node,
        "affected_technology":
            affected_technology,

        "hostname_mismatch":
            hostname_mismatch,

        "port_matches":
            port_matches,

        "relevant_edges":
            relevant_edges,
    }
