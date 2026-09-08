export type GraphNode = {
  id: string;
  type: string;
  technology: string;
};

export type GraphEdge = {
  source: string;
  target: string;
  type: string;
};

export type AnalysisResult = {
  root_cause: string;
  confidence: number;
  explanation: string;
  evidence: string[];
  recommended_fixes: string[];
  verification_steps: string[];

  affected_node: string | null;
  affected_technology: string | null;
  graph_confidence: number;

  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
};