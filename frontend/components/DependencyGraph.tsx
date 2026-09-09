"use client";

import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  Position,
  type Node,
  type Edge,
} from "@xyflow/react";

import dagre from "@dagrejs/dagre";

import "@xyflow/react/dist/style.css";

import type { AnalysisResult } from "@/types/analysis";

type Props = {
  graph: AnalysisResult["graph"];
  affectedNode: string | null;
};

const NODE_WIDTH = 180;
const NODE_HEIGHT = 80;

function getLayoutedElements(nodes: Node[], edges: Edge[]) {
  const dagreGraph = new dagre.graphlib.Graph();

  dagreGraph.setDefaultEdgeLabel(() => ({}));

  dagreGraph.setGraph({
    rankdir: "LR",
    ranksep: 100,
    nodesep: 60,
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: NODE_WIDTH,
      height: NODE_HEIGHT,
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const position = dagreGraph.node(node.id);

    return {
      ...node,

      position: {
        x: position.x - NODE_WIDTH / 2,

        y: position.y - NODE_HEIGHT / 2,
      },

      sourcePosition: Position.Right,

      targetPosition: Position.Left,
    };
  });

  return {
    nodes: layoutedNodes,
    edges,
  };
}

export default function DependencyGraph({ graph, affectedNode }: Props) {
  const initialNodes: Node[] = graph.nodes.map((node) => {
    const isAffected = node.id === affectedNode;

    return {
      id: node.id,

      position: {
        x: 0,
        y: 0,
      },

      data: {
        label: (
          <div className="text-center">
            <div className="font-semibold">{node.id}</div>

            <div className="text-xs text-gray-300">{node.technology}</div>

            {isAffected && (
              <div className="mt-2 rounded bg-red-950 px-2 py-1 text-xs font-medium text-red-300">
                Suspected component
              </div>
            )}
          </div>
        ),
      },

      style: {
        border: isAffected ? "2px solid #ef4444" : "1px solid #4b5563",

        background: isAffected ? "#450a0a" : "#111827",

        color: "#ffffff",

        borderRadius: 10,

        padding: 12,

        width: NODE_WIDTH,

        boxShadow: isAffected
          ? "0 0 18px rgba(239, 68, 68, 0.25)"
          : "0 4px 12px rgba(0, 0, 0, 0.25)",
      },
    };
  });

  const initialEdges: Edge[] = graph.edges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,

    source: edge.source,

    target: edge.target,

    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: "#94a3b8",
    },

    style: {
      strokeWidth: 1.5,
      stroke: "#94a3b8",
    },
  }));

  const { nodes, edges } = getLayoutedElements(initialNodes, initialEdges);

  return (
    <div className="h-[380px] w-full overflow-hidden rounded-xl border border-gray-800 bg-gray-950 shadow-inner sm:h-[500px]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{
          padding: 0.2,
        }}
        minZoom={0.4}
        maxZoom={1.8}
      >
        <Background gap={20} size={1} color="#374151" />

        <Controls className="!border-gray-700 !bg-gray-900 !text-white" />

        <MiniMap
          pannable
          zoomable
          position="bottom-right"
          className="!h-28 !w-40 !border !border-gray-700 !bg-gray-900"
          nodeColor={(node) => {
            if (node.id === affectedNode) {
              return "#ef4444";
            }

            return "#374151";
          }}
          nodeStrokeColor={(node) => {
            if (node.id === affectedNode) {
              return "#f87171";
            }

            return "#6b7280";
          }}
          nodeStrokeWidth={2}
          maskColor="rgba(3, 7, 18, 0.7)"
        />
      </ReactFlow>
    </div>
  );
}
