import type { AnalysisResult } from "@/types/analysis";
import DependencyGraph from "@/components/DependencyGraph";
import FeedbackControls from "@/components/FeedbackControls";

type Props = {
  result: AnalysisResult;
};

export default function AnalysisPanel({ result }: Props) {
  return (
    <div className="space-y-6">
      {/* Root Cause */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">Root Cause</h2>

        <p className="mt-3 text-lg">
          {result.root_cause}
        </p>

        <p className="mt-2 text-sm text-gray-400">
          Confidence:{" "}
          {Math.round(result.confidence * 100)}%
        </p>
      </section>

      {/* Affected Component */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">
              Affected Component
            </h2>

            <p className="mt-1 text-sm text-gray-400">
              Component most closely associated with the error
            </p>
          </div>

          <span className="rounded-full border border-red-800 bg-red-950 px-3 py-1 text-xs font-medium text-red-300">
            Suspected
          </span>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Component
            </p>

            <p className="mt-2 font-semibold">
              {result.affected_node ?? "Unknown"}
            </p>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Technology
            </p>

            <p className="mt-2 font-semibold">
              {result.affected_technology ?? "Unknown"}
            </p>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">
              Graph Confidence
            </p>

            <p className="mt-2 font-semibold">
              {Math.round(
                result.graph_confidence * 100
              )}
              %
            </p>
          </div>
        </div>
      </section>

      {/* Explanation */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">
          Explanation
        </h2>

        <p className="mt-3 text-gray-300">
          {result.explanation}
        </p>
      </section>

      {/* Dependency Graph */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-xl font-semibold">
          Dependency Graph
        </h2>

        <p className="mt-2 text-sm text-gray-400">
          Highlighted node indicates the component most closely associated
          with the error.
        </p>

        <div className="mt-3 flex items-center gap-5 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-sm border border-gray-500 bg-gray-800" />
            Service
          </div>

          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-sm border border-red-500 bg-red-950" />
            Suspected component
          </div>
        </div>

        <div className="mt-4">
          <DependencyGraph
            graph={result.graph}
            affectedNode={result.affected_node}
          />
        </div>
      </section>

      {/* Evidence */}
      <ListSection
        title="Evidence"
        items={result.evidence}
      />

      {/* Recommended Fixes */}
      <ListSection
        title="Recommended Fixes"
        items={result.recommended_fixes}
      />

      {/* Verification Steps */}
      <ListSection
        title="Verification Steps"
        items={result.verification_steps}
      />

      <FeedbackControls />
    </div>
  );
}

function ListSection({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <h2 className="text-xl font-semibold">
        {title}
      </h2>

      <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-300">
        {items.map((item, index) => (
          <li key={index}>
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}