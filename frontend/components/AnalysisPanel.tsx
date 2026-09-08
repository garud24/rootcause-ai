import { AnalysisResult } from "@/types/analysis";
import DependencyGraph from "@/components/DependencyGraph";
type Props = {
  result: AnalysisResult;
};

export default function AnalysisPanel({ result }: Props) {
  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">Root Cause</h2>

        <p className="mt-3 text-lg">{result.root_cause}</p>

        <p className="mt-2 text-sm text-gray-400">
          Confidence: {Math.round(result.confidence * 100)}%
        </p>
      </section>

      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">Explanation</h2>

        <p className="mt-3 text-gray-300">{result.explanation}</p>
      </section>

      <ListSection title="Evidence" items={result.evidence} />

      <ListSection title="Recommended Fixes" items={result.recommended_fixes} />

      <ListSection
        title="Verification Steps"
        items={result.verification_steps}
      />

      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">Dependency Graph</h2>

        <p className="mt-2 text-sm text-gray-400">
          Highlighted node indicates the component most closely associated with
          the error.
        </p>

        <div className="mt-4">
          <DependencyGraph
            graph={result.graph}
            affectedNode={result.affected_node}
          />
        </div>
      </section>
    </div>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <h2 className="text-xl font-semibold">{title}</h2>

      <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-300">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
