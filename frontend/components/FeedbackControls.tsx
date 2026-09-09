"use client";

import { useState } from "react";

type FeedbackValue =
  | "positive"
  | "negative"
  | null;

export default function FeedbackControls() {
  const [feedback, setFeedback] =
    useState<FeedbackValue>(null);

  return (
    <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <h2 className="text-xl font-semibold">
        Was this diagnosis helpful?
      </h2>

      <p className="mt-2 text-sm text-gray-400">
        Your feedback will help improve future diagnoses.
      </p>

      <div className="mt-5 flex gap-3">
        <button
          onClick={() =>
            setFeedback("positive")
          }
          className={`rounded-lg border px-4 py-2 text-sm font-medium transition ${
            feedback === "positive"
              ? "border-green-600 bg-green-950 text-green-300"
              : "border-gray-700 bg-gray-950 text-gray-300 hover:bg-gray-800"
          }`}
        >
          👍 Solved
        </button>

        <button
          onClick={() =>
            setFeedback("negative")
          }
          className={`rounded-lg border px-4 py-2 text-sm font-medium transition ${
            feedback === "negative"
              ? "border-red-600 bg-red-950 text-red-300"
              : "border-gray-700 bg-gray-950 text-gray-300 hover:bg-gray-800"
          }`}
        >
          👎 Didn&apos;t help
        </button>
      </div>

      {feedback && (
        <p className="mt-4 text-sm text-gray-400">
          Thanks for the feedback.
        </p>
      )}
    </section>
  );
}