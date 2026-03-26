"use client";

interface ProgressTrackerProps {
  stage: string;
  detail: string;
  completed: number;
  total: number;
}

const STAGE_LABELS: Record<string, string> = {
  waiting: "Preparing...",
  voiceover: "Generating Voiceovers",
  music: "Generating Background Music",
  clips: "Generating Video Clips",
  qa: "Running Quality Checks",
  stitching: "Stitching Final Videos",
  uploading: "Uploading Videos",
  complete: "Complete!",
  error: "Error",
};

const STAGE_ORDER = [
  "voiceover",
  "music",
  "clips",
  "qa",
  "stitching",
  "uploading",
  "complete",
];

export default function ProgressTracker({
  stage,
  detail,
  completed,
  total,
}: ProgressTrackerProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const currentStageIndex = STAGE_ORDER.indexOf(stage);

  return (
    <div className="flex flex-col gap-8">
      <div className="text-center">
        <h2 className="mb-2 text-xl font-semibold">
          {STAGE_LABELS[stage] || stage}
        </h2>
        <p className="text-sm text-gray-500">{detail}</p>
      </div>

      {/* Progress bar */}
      <div className="mx-auto w-full max-w-md">
        <div className="mb-2 flex justify-between text-xs text-gray-400">
          <span>Progress</span>
          <span>{percentage}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full rounded-full bg-gray-900 transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Stage checklist */}
      <div className="mx-auto flex w-full max-w-sm flex-col gap-3">
        {STAGE_ORDER.map((s, i) => {
          const isDone = currentStageIndex > i || stage === "complete";
          const isCurrent = s === stage;

          return (
            <div key={s} className="flex items-center gap-3">
              {isDone ? (
                <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : isCurrent ? (
                <svg className="h-5 w-5 animate-spin text-gray-400" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-200" />
              )}
              <span
                className={`text-sm ${
                  isDone
                    ? "text-green-600"
                    : isCurrent
                    ? "font-medium text-gray-900"
                    : "text-gray-400"
                }`}
              >
                {STAGE_LABELS[s]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
