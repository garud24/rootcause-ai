"use client";

import { useState } from "react";

type AnalysisResult = {
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
    nodes: {
      id: string;
      type: string;
      technology: string;
    }[];
    edges: {
      source: string;
      target: string;
      type: string;
    }[];
  };
};

export default function Home() {
  const [repositoryUrl, setRepositoryUrl] =
    useState("");

  const [errorText, setErrorText] =
    useState("");

  const [result, setResult] =
    useState<AnalysisResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/analyze/repository",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_url: repositoryUrl,
            error_text: errorText,
          }),
        }
      );

      if (!response.ok) {
        const body = await response.json();

        throw new Error(
          body.detail ||
            "Analysis request failed"
        );
      }

      const data: AnalysisResult =
        await response.json();

      setResult(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "An unexpected error occurred"
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <div className="mx-auto max-w-5xl px-6 py-12">
        <h1 className="text-4xl font-bold">
          RootCause AI
        </h1>

        <p className="mt-3 text-gray-400">
          Paste the error. Find the cause.
          Fix it faster.
        </p>

        <div className="mt-10 space-y-6">
          <div>
            <label className="mb-2 block text-sm font-medium">
              GitHub Repository
            </label>

            <input
              type="text"
              value={repositoryUrl}
              onChange={(event) =>
                setRepositoryUrl(
                  event.target.value
                )
              }
              placeholder="https://github.com/owner/repository"
              className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 outline-none focus:border-gray-500"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Error or Stack Trace
            </label>

            <textarea
              value={errorText}
              onChange={(event) =>
                setErrorText(
                  event.target.value
                )
              }
              placeholder="Error: connect ECONNREFUSED 127.0.0.1:5432"
              rows={8}
              className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 font-mono outline-none focus:border-gray-500"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={
              loading ||
              !repositoryUrl ||
              !errorText
            }
            className="rounded-lg bg-white px-6 py-3 font-medium text-black disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Analyzing..."
              : "Analyze Error"}
          </button>

          {error && (
            <div className="rounded-lg border border-red-900 bg-red-950 p-4 text-red-300">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-10 space-y-6">
              <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="text-xl font-semibold">
                  Root Cause
                </h2>

                <p className="mt-3 text-lg">
                  {result.root_cause}
                </p>

                <p className="mt-2 text-sm text-gray-400">
                  Confidence:{" "}
                  {Math.round(
                    result.confidence *
                      100
                  )}
                  %
                </p>
              </section>

              <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="text-xl font-semibold">
                  Explanation
                </h2>

                <p className="mt-3 text-gray-300">
                  {result.explanation}
                </p>
              </section>

              <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="text-xl font-semibold">
                  Evidence
                </h2>

                <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-300">
                  {result.evidence.map(
                    (item, index) => (
                      <li key={index}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              </section>

              <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="text-xl font-semibold">
                  Recommended Fixes
                </h2>

                <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-300">
                  {result.recommended_fixes.map(
                    (item, index) => (
                      <li key={index}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              </section>

              <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
                <h2 className="text-xl font-semibold">
                  Verification Steps
                </h2>

                <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-300">
                  {result.verification_steps.map(
                    (item, index) => (
                      <li key={index}>
                        {item}
                      </li>
                    )
                  )}
                </ul>
              </section>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}