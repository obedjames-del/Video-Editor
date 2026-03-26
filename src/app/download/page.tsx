"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import VideoDownloader from "@/components/VideoDownloader";

function DownloadContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session");

  const [videoUrls, setVideoUrls] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;

    async function load() {
      try {
        const res = await fetch(`/api/status?session=${sessionId}`);
        if (!res.ok) throw new Error("Failed to load results");
        const data = await res.json();

        if (data.videoUrls) {
          setVideoUrls(data.videoUrls);
        } else {
          throw new Error("Videos not ready yet");
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load videos");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [sessionId]);

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
        <p className="text-sm text-gray-500">Loading videos...</p>
      </div>
    );
  }

  if (error) return <p className="text-center text-red-500">{error}</p>;
  if (!videoUrls) return <p className="text-center text-gray-500">No videos found.</p>;

  return (
    <div className="pt-8">
      <VideoDownloader videoUrls={videoUrls} />
    </div>
  );
}

export default function DownloadPage() {
  return (
    <Suspense fallback={<div className="text-center text-gray-500">Loading...</div>}>
      <DownloadContent />
    </Suspense>
  );
}
