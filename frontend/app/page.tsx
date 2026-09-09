"use client";

import { useState } from "react";

import RepositoryInput from "@/components/RepositoryInput";
import ErrorInput from "@/components/ErrorInput";
import AnalysisPanel from "@/components/AnalysisPanel";
import LoadingAnalysis from "@/components/LoadingAnalysis";

import type { AnalysisResult } from "@/types/analysis";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function Home() {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [errorText, setErrorText] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/analyze/repository`,
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
        let message = "Analysis request failed";

        try {
          const body = await response.json();

          if (typeof body.detail === "string") {
            message = body.detail;
          }
        } catch {
          // The response body was not valid JSON.
        }

        throw new Error(message);
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

  function handleReset() {
    setRepositoryUrl("");
    setErrorText("");
    setResult(null);
    setError(null);
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
          <RepositoryInput
            value={repositoryUrl}
            onChange={setRepositoryUrl}
          />

          <ErrorInput
            value={errorText}
            onChange={setErrorText}
          />

          <div className="flex gap-3">
            <button
              onClick={handleAnalyze}
              disabled={
                loading ||
                !repositoryUrl ||
                !errorText
              }
              className="rounded-lg bg-white px-6 py-3 font-medium text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Analyzing..."
                : "Analyze Error"}
            </button>

            <button
              onClick={handleReset}
              disabled={loading}
              className="rounded-lg border border-gray-700 bg-gray-900 px-6 py-3 font-medium text-gray-200 transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Clear
            </button>
          </div>

          {error && (
            <div className="rounded-xl border border-red-900 bg-red-950 p-5">
              <h2 className="font-semibold text-red-300">
                Analysis failed
              </h2>

              <p className="mt-2 text-sm text-red-200">
                {error}
              </p>

              <p className="mt-3 text-xs text-red-400">
                Check the repository URL,
                backend status, and local model
                availability, then try again.
              </p>
            </div>
          )}

          {loading && (
            <LoadingAnalysis />
          )}

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