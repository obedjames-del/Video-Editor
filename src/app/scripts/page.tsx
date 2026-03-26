"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import ScriptViewer from "@/components/ScriptViewer";
import { GeneratedScript } from "@/lib/ai/script-generator";

function ScriptsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");

  const [scripts, setScripts] = useState<GeneratedScript[] | null>(null);
  const [generating, setGenerating] = useState(true);
  const [storyboardLoading, setStoryboardLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;

    async function generate() {
      try {
        // Try to load existing scripts first
        const getRes = await fetch(`/api/scripts?session=${sessionId}`);
        if (getRes.ok) {
          const data = await getRes.json();
          setScripts(data.scripts);
          setGenerating(false);
          return;
        }

        // Generate new scripts
        const res = await fetch("/api/scripts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessionId }),
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error || "Script generation failed");
        }

        const data = await res.json();
        setScripts(data.scripts);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to generate scripts");
      } finally {
        setGenerating(false);
      }
    }

    generate();
  }, [sessionId]);

  const handleApprove = async () => {
    setStoryboardLoading(true);
    try {
      const res = await fetch("/api/storyboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Storyboard generation failed");
      }

      router.push(`/storyboard?session=${sessionId}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to generate storyboard");
      setStoryboardLoading(false);
    }
  };

  if (!sessionId) {
    return <p className="text-center text-gray-500">No session found. Please upload a file first.</p>;
  }

  if (generating) {
    return (
      <div className="flex flex-col items-center gap-4 pt-20">
        <svg className="h-8 w-8 animate-spin text-gray-400" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p className="text-sm text-gray-500">Generating scripts from your slides...</p>
      </div>
    );
  }

  if (error) {
    return <p className="text-center text-red-500">{error}</p>;
  }

  if (!scripts) {
    return <p className="text-center text-gray-500">No scripts generated.</p>;
  }

  return (
    <ScriptViewer
      scripts={scripts}
      onApprove={handleApprove}
      loading={storyboardLoading}
    />
  );
}

export default function ScriptsPage() {
  return (
    <Suspense fallback={<div className="text-center text-gray-500">Loading...</div>}>
      <ScriptsContent />
    </Suspense>
  );
}
