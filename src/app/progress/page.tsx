"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import ProgressTracker from "@/components/ProgressTracker";

interface ProgressState {
  stage: string;
  detail: string;
  completed: number;
  total: number;
  videoUrls?: string[];
  error?: string;
}

function ProgressContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");

  const [progress, setProgress] = useState<ProgressState>({
    stage: "waiting",
    detail: "Preparing...",
    completed: 0,
    total: 0,
  });

  useEffect(() => {
    if (!sessionId) return;

    const poll = setInterval(async () => {
      try {
        const res = await fetch(`/api/status?session=${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          setProgress(data);

          if (data.stage === "complete") {
            clearInterval(poll);
            setTimeout(() => {
              router.push(`/download?session=${sessionId}`);
            }, 2000);
          }

          if (data.stage === "error") {
            clearInterval(poll);
          }
        }
      } catch {
        // Ignore polling errors
      }
    }, 3000);

    return () => clearInterval(poll);
  }, [sessionId, router]);

  if (!sessionId) {
    return <p className="text-center text-gray-500">No session found.</p>;
  }

  if (progress.error) {
    return (
      <div className="flex flex-col items-center gap-4 pt-20">
        <p className="text-red-500">Error: {progress.error}</p>
        <button
          onClick={() => router.push("/")}
          className="rounded-lg bg-gray-900 px-6 py-2 text-sm text-white hover:bg-gray-800"
        >
          Start Over
        </button>
      </div>
    );
  }

  return (
    <div className="pt-12">
      <ProgressTracker
        stage={progress.stage}
        detail={progress.detail}
        completed={progress.completed}
        total={progress.total}
      />
    </div>
  );
}

export default function ProgressPage() {
  return (
    <Suspense fallback={<div className="text-center text-gray-500">Loading...</div>}>
      <ProgressContent />
    </Suspense>
  );
}
