"use client";

import { useState } from "react";

import RepositoryInput from "@/components/RepositoryInput";
import ErrorInput from "@/components/ErrorInput";
import AnalysisPanel from "@/components/AnalysisPanel";

import { AnalysisResult } from "@/types/analysis";

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

          {/* Repository input component */}
          <RepositoryInput
            value={repositoryUrl}
            onChange={setRepositoryUrl}
          />

          {/* Error input component */}
          <ErrorInput
            value={errorText}
            onChange={setErrorText}
          />

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

          {/* Analysis result component */}
          {result && (
            <div className="mt-10">
              <AnalysisPanel
                result={result}
              />
            </div>
          )}

        </div>
      </div>
    </main>
  );
}