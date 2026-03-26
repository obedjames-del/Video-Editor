import { NextRequest, NextResponse } from "next/server";
import { readFile, writeFile, mkdir } from "fs/promises";
import path from "path";
import { generateAllClips } from "@/lib/video/veo-client";
import { generateVoiceover, generateBackgroundMusic } from "@/lib/video/elevenlabs-client";
import { qaCheckAllClips } from "@/lib/video/vision-qa";
import { stitchAllVideos } from "@/lib/video/ffmpeg-stitcher";
import { uploadAllVideos } from "@/lib/storage/gcs-client";
import { Storyboard } from "@/lib/ai/storyboard-generator";
import { GeneratedScript } from "@/lib/ai/script-generator";

interface ProgressState {
  stage: string;
  detail: string;
  completed: number;
  total: number;
  videoUrls?: string[];
  error?: string;
}

async function updateProgress(sessionDir: string, progress: ProgressState) {
  await writeFile(
    path.join(sessionDir, "progress.json"),
    JSON.stringify(progress, null, 2)
  );
}

export async function POST(req: NextRequest) {
  const { sessionId } = await req.json();
  if (!sessionId) {
    return NextResponse.json({ error: "Missing sessionId" }, { status: 400 });
  }

  const sessionDir = path.join(process.cwd(), "tmp", sessionId);
  const outputDir = path.join(sessionDir, "output");
  await mkdir(outputDir, { recursive: true });

  // Start generation in background (non-blocking)
  runPipeline(sessionId, sessionDir, outputDir).catch((err) => {
    console.error("Pipeline error:", err);
    updateProgress(sessionDir, {
      stage: "error",
      detail: err instanceof Error ? err.message : "Pipeline failed",
      completed: 0,
      total: 0,
      error: err instanceof Error ? err.message : "Pipeline failed",
    });
  });

  return NextResponse.json({ status: "started" });
}

async function runPipeline(
  sessionId: string,
  sessionDir: string,
  outputDir: string
) {
  const storyboards: Storyboard[] = JSON.parse(
    await readFile(path.join(sessionDir, "storyboards.json"), "utf-8")
  );
  const scripts: GeneratedScript[] = JSON.parse(
    await readFile(path.join(sessionDir, "scripts.json"), "utf-8")
  );

  const totalScenes = storyboards.reduce((sum, sb) => sum + sb.scenes.length, 0);
  const totalSteps = totalScenes + scripts.length * 2 + totalScenes + scripts.length; // clips + voice + music + qa + stitch
  let completedSteps = 0;

  // Step 1: Generate voiceovers (parallel per video)
  await updateProgress(sessionDir, {
    stage: "voiceover",
    detail: "Generating voiceovers...",
    completed: 0,
    total: totalSteps,
  });

  const voiceovers = await Promise.all(
    scripts.map((script) =>
      generateVoiceover(script.script, script.videoNumber, outputDir)
    )
  );
  completedSteps += scripts.length;

  // Step 2: Generate background music (parallel per video)
  await updateProgress(sessionDir, {
    stage: "music",
    detail: "Generating background music...",
    completed: completedSteps,
    total: totalSteps,
  });

  // Estimate total duration from scenes (8s each minus transitions)
  const musicResults = await Promise.all(
    storyboards.map((sb, i) => {
      const duration = sb.scenes.length * 7; // ~7s per scene with overlap
      return generateBackgroundMusic(
        scripts[i].title,
        sb.videoNumber,
        duration,
        outputDir
      );
    })
  );
  completedSteps += scripts.length;

  // Step 3: Generate video clips
  const allClipResults: { videoNumber: number; clipPaths: string[] }[] = [];

  for (const sb of storyboards) {
    await updateProgress(sessionDir, {
      stage: "clips",
      detail: `Generating video clips for Video ${sb.videoNumber}...`,
      completed: completedSteps,
      total: totalSteps,
    });

    const clipDir = path.join(outputDir, `video_${sb.videoNumber}`);
    await mkdir(clipDir, { recursive: true });

    const results = await generateAllClips(sb.scenes, clipDir, (done, total) => {
      updateProgress(sessionDir, {
        stage: "clips",
        detail: `Video ${sb.videoNumber}: clip ${done}/${total}`,
        completed: completedSteps + done,
        total: totalSteps,
      });
    });

    const clipPaths = results.filter((r) => r.success).map((r) => r.videoPath);
    allClipResults.push({ videoNumber: sb.videoNumber, clipPaths });
    completedSteps += sb.scenes.length;
  }

  // Step 4: QA Check
  await updateProgress(sessionDir, {
    stage: "qa",
    detail: "Running quality checks...",
    completed: completedSteps,
    total: totalSteps,
  });

  for (const { videoNumber, clipPaths } of allClipResults) {
    const clips = clipPaths.map((p, i) => ({ sceneNumber: i + 1, videoPath: p }));
    const qaResults = await qaCheckAllClips(clips);

    // Log QA results
    await writeFile(
      path.join(outputDir, `qa_video_${videoNumber}.json`),
      JSON.stringify(qaResults, null, 2)
    );
    completedSteps += clipPaths.length;
  }

  // Step 5: Stitch videos
  await updateProgress(sessionDir, {
    stage: "stitching",
    detail: "Stitching final videos...",
    completed: completedSteps,
    total: totalSteps,
  });

  const stitchData = allClipResults.map(({ videoNumber, clipPaths }) => ({
    videoNumber,
    clipPaths,
    voiceoverPath: voiceovers.find((v) => v.videoNumber === videoNumber)?.audioPath || "",
    musicPath: musicResults.find((m) => m.videoNumber === videoNumber)?.musicPath || "",
  }));

  const finalPaths = await stitchAllVideos(stitchData, outputDir, (vn) => {
    completedSteps++;
    updateProgress(sessionDir, {
      stage: "stitching",
      detail: `Stitched Video ${vn}`,
      completed: completedSteps,
      total: totalSteps,
    });
  });

  // Step 6: Upload to GCS
  await updateProgress(sessionDir, {
    stage: "uploading",
    detail: "Uploading final videos...",
    completed: completedSteps,
    total: totalSteps,
  });

  let videoUrls: string[];
  try {
    videoUrls = await uploadAllVideos(finalPaths, sessionId);
  } catch {
    // Fallback: serve locally if GCS isn't configured
    videoUrls = finalPaths.map(
      (p) => `/api/download?session=${sessionId}&file=${path.basename(p)}`
    );
  }

  // Done!
  await updateProgress(sessionDir, {
    stage: "complete",
    detail: "All videos ready!",
    completed: totalSteps,
    total: totalSteps,
    videoUrls,
  });

  // Save final URLs
  await writeFile(
    path.join(sessionDir, "results.json"),
    JSON.stringify({ videoUrls, finalPaths }, null, 2)
  );
}
