export default function LoadingAnalysis() {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-8">
      <div className="flex items-center gap-4">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-600 border-t-white" />

        <div>
          <h2 className="font-semibold">
            Analyzing repository
          </h2>

          <p className="mt-1 text-sm text-gray-400">
            Inspecting repository context and generating a grounded diagnosis.
          </p>
        </div>
      </div>

      <div className="mt-6 h-1 overflow-hidden rounded-full bg-gray-800">
        <div className="h-full w-1/3 animate-pulse rounded-full bg-gray-400" />
      </div>
    </div>
  );
}