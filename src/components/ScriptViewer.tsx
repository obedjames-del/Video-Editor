"use client";

import { GeneratedScript } from "@/lib/ai/script-generator";

interface ScriptViewerProps {
  scripts: GeneratedScript[];
  onApprove: () => void;
  loading?: boolean;
}

export default function ScriptViewer({
  scripts,
  onApprove,
  loading,
}: ScriptViewerProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Review Generated Scripts</h2>
        <span className="text-sm text-gray-400">{scripts.length} videos</span>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {scripts.map((script) => (
          <div
            key={script.videoNumber}
            className="flex flex-col rounded-xl border border-gray-200 bg-white p-5"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-600">
                Video {script.videoNumber}
              </span>
              <span className="text-xs text-gray-400">
                {script.slideRange}
              </span>
            </div>
            <h3 className="mb-3 text-sm font-semibold">{script.title}</h3>
            <div className="flex-1 overflow-y-auto">
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-600">
                {script.script}
              </p>
            </div>
            <div className="mt-3 border-t border-gray-100 pt-3">
              <p className="text-xs text-gray-400">
                ~{Math.ceil(script.script.split(" ").length / 150)} min read
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-center pt-4">
        <button
          onClick={onApprove}
          disabled={loading}
          className="rounded-lg bg-gray-900 px-8 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Generating Storyboard..." : "Generate Storyboard"}
        </button>
      </div>
    </div>
  );
}
