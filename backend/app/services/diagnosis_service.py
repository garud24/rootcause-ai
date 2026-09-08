from app.services.github_service import (
    get_repository_tree,
    detect_important_files,
    get_file_content,
)

from app.services.repository_analyzer import (
    analyze_file,
)

from app.services.docker_compose_analyzer import (
    analyze_docker_compose,
)

from app.services.graph_builder import (
    build_graph,
)

from app.services.error_graph_matcher import (
    match_error_to_graph,
)

from app.services.ollama_service import (
    analyze_with_ollama,
)

from app.services.configuration_analyzer import (
    extract_compose_configuration,
)

COMPOSE_FILENAMES = {
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "compose.override.yml",
    "compose.override.yaml",
    "compose.deploy.yml",
    "compose.deploy.yaml",
}

def build_repository_context(
    technologies: list[str],
    graph: dict,
    graph_diagnosis: dict,
    configuration_evidence: list[str],
) -> str:

    lines = []

    if technologies:
        lines.append(
            "Detected technologies: "
            + ", ".join(technologies)
        )

    affected_node = graph_diagnosis.get(
        "affected_node"
    )

    affected_technology = graph_diagnosis.get(
        "technology"
    )

    graph_confidence = graph_diagnosis.get(
        "confidence",
        0.0,
    )

    if affected_node:
        lines.append(
            f"Suspected affected node: "
            f"{affected_node}"
        )

    if affected_technology:
        lines.append(
            f"Suspected technology: "
            f"{affected_technology}"
        )

    lines.append(
        f"Graph match confidence: "
        f"{graph_confidence}"
    )

    if affected_node:

        relevant_edges = []

        for edge in graph.get("edges", []):

            if (
                edge.get("source")
                == affected_node
                or edge.get("target")
                == affected_node
            ):
                relevant_edges.append(edge)

        if relevant_edges:

            lines.append(
                "Relevant architecture relationships:"
            )

            for edge in relevant_edges:

                lines.append(
                    f"- {edge['source']} "
                    f"--{edge['type']}--> "
                    f"{edge['target']}"
                )
            
            if configuration_evidence:
                
                lines.append(
                    "Repository configuration evidence:"
                )
                for item in configuration_evidence:
                    lines.append(
                        f"- {item}"
                    )    

    return "\n".join(lines)

async def diagnose_repository(
    repository_url: str,
    error_text: str,
) -> dict:

    # 1. Get repository tree
    tree = await get_repository_tree(
        repository_url
    )

    # 2. Find important files
    important_files = detect_important_files(
        tree
    )

    technologies = set()
    configuration_evidence = []
    compose_graph = {
        "nodes": [],
        "edges": [],
    }

    # 3. Analyze repository files
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

        # 4. Parse Docker Compose
        if filename in COMPOSE_FILENAMES:

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
            config_evidence = (
            extract_compose_configuration(
            content
                )
            )

            configuration_evidence.extend(
                config_evidence
            )

    # 5. Remove duplicate nodes
    unique_nodes = {}

    for node in compose_graph["nodes"]:
        unique_nodes[node["id"]] = node

    # 6. Remove duplicate edges
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

    # 7. Build final architecture graph
    graph = build_graph(
        sorted(technologies),
        compose_graph,
    )

    # 8. Match error to graph
    graph_diagnosis = match_error_to_graph(
        error_text,
        graph,
    )

    # 9. Ask Ollama for root-cause analysis
    repository_context = build_repository_context(
    technologies=sorted(technologies),
    graph=graph,
    graph_diagnosis=graph_diagnosis,
    configuration_evidence=configuration_evidence,
    )
    print("REPOSITORY CONTEXT SENT TO OLLAMA:")
    print(repository_context)
    
    llm_analysis = await analyze_with_ollama(
    error_text=error_text,
    repository_context=repository_context,
    )


    # 10. Merge everything
    return {
        "root_cause": llm_analysis[
            "root_cause"
        ],
        "confidence": llm_analysis[
            "confidence"
        ],
        "explanation": llm_analysis[
            "explanation"
        ],
        "evidence": llm_analysis[
            "evidence"
        ],
        "recommended_fixes": llm_analysis[
            "recommended_fixes"
        ],
        "verification_steps": llm_analysis[
            "verification_steps"
        ],

        "affected_node": graph_diagnosis[
            "affected_node"
        ],
        "affected_technology": (
            graph_diagnosis[
                "technology"
            ]
        ),
        "graph_confidence": (
            graph_diagnosis[
                "confidence"
            ]
        ),

        "graph": graph,
    }