"use client";

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import type { AnalysisResult } from "@/types/analysis";

type Props = {
  graph: AnalysisResult["graph"];
  affectedNode: string | null;
};

export default function DependencyGraph({
  graph,
  affectedNode,
}: Props) {
  const nodes: Node[] = graph.nodes.map(
    (node, index) => ({
      id: node.id,

      position: {
        x: (index % 3) * 250,
        y: Math.floor(index / 3) * 180,
      },

      data: {
        label: `${node.id}\n${node.technology}`,
      },

      style: {
        border:
          node.id === affectedNode
            ? "2px solid #ef4444"
            : "1px solid #4b5563",

        background:
          node.id === affectedNode
            ? "#450a0a"
            : "#111827",

        color: "#ffffff",

        padding: 12,

        borderRadius: 8,

        width: 180,

        whiteSpace: "pre-line",
      },
    })
  );

  const edges: Edge[] = graph.edges.map(
    (edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
    })
  );

  return (
    <div className="h-[500px] w-full rounded-xl border border-gray-800 bg-gray-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >
        <Background />

        <Controls />

        <MiniMap />
      </ReactFlow>
    </div>
  );
}