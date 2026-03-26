"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import StoryboardEditor from "@/components/StoryboardEditor";
import { Storyboard } from "@/lib/ai/storyboard-generator";

function StoryboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");

  const [storyboards, setStoryboards] = useState<Storyboard[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;

    async function load() {
      try {
        const res = await fetch(`/api/storyboard?session=${sessionId}`);
        if (!res.ok) throw new Error("Failed to load storyboards");
        const data = await res.json();
        setStoryboards(data.storyboards);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load storyboards");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [sessionId]);

  const handleSave = async (updated: Storyboard[]) => {
    await fetch("/api/storyboard", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, storyboards: updated }),
    });
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Generation failed");
      }

      router.push(`/progress?session=${sessionId}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setGenerating(false);
    }
  };

  if (!sessionId) {
    return <p className="text-center text-gray-500">No session found.</p>;
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center gap-4 pt-20">
        <svg className="h-8 w-8 animate-spin text-gray-400" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p className="text-sm text-gray-500">Loading storyboard...</p>
      </div>
    );
  }

  if (error) return <p className="text-center text-red-500">{error}</p>;
  if (!storyboards) return <p className="text-center text-gray-500">No storyboard data.</p>;

  return (
    <StoryboardEditor
      storyboards={storyboards}
      onSave={handleSave}
      onGenerate={handleGenerate}
      generating={generating}
    />
  );
}

export default function StoryboardPage() {
  return (
    <Suspense fallback={<div className="text-center text-gray-500">Loading...</div>}>
      <StoryboardContent />
    </Suspense>
  );
}
