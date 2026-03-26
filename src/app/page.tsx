"use client";

import { useRouter } from "next/navigation";
import UploadZone from "@/components/UploadZone";

export default function Home() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center gap-8 pt-12">
      <div className="text-center">
        <h2 className="mb-2 text-3xl font-bold tracking-tight">
          Sermon Video Generator
        </h2>
        <p className="text-base text-gray-500">
          Upload your PowerPoint slides and we&apos;ll generate 3 short teaching
          videos with AI narration, visuals, and music.
        </p>
      </div>

      <UploadZone
        onUploadComplete={(sessionId) => {
          router.push(`/scripts?session=${sessionId}`);
        }}
      />

      <div className="mt-8 grid max-w-2xl grid-cols-3 gap-6 text-center text-sm text-gray-400">
        <div>
          <div className="mb-1 text-2xl">1</div>
          <p>Upload sermon slides</p>
        </div>
        <div>
          <div className="mb-1 text-2xl">2</div>
          <p>Review scripts &amp; storyboard</p>
        </div>
        <div>
          <div className="mb-1 text-2xl">3</div>
          <p>Download 3 videos</p>
        </div>
      </div>
    </div>
  );
}
