import { execSync } from "child_process";
import { writeFile } from "fs/promises";
import path from "path";

export interface StitchConfig {
  clipPaths: string[];
  voiceoverPath: string;
  musicPath: string;
  outputPath: string;
  dissolveFrames?: number;
}

export async function stitchVideo(config: StitchConfig): Promise<string> {
  const { clipPaths, voiceoverPath, musicPath, outputPath, dissolveFrames = 15 } = config;
  const dir = path.dirname(outputPath);

  // Step 1: Create a concat file with crossfade transitions
  if (clipPaths.length === 1) {
    // Single clip, just copy
    const filterComplex = `[0:v]format=yuv420p[outv]`;
    const cmd = `ffmpeg -y -i "${clipPaths[0]}" -i "${voiceoverPath}" -i "${musicPath}" -filter_complex "${filterComplex};[1:a]volume=1.0[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=longest[outa]" -map "[outv]" -map "[outa]" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -shortest "${outputPath}" 2>&1`;
    execSync(cmd, { cwd: dir, maxBuffer: 50 * 1024 * 1024 });
    return outputPath;
  }

  // Step 2: Build crossfade filter chain for multiple clips
  const fadeDuration = dissolveFrames / 30; // assuming 30fps
  let filterParts: string[] = [];
  let lastLabel = "[0:v]";

  for (let i = 1; i < clipPaths.length; i++) {
    const outLabel = i === clipPaths.length - 1 ? "[outv]" : `[v${i}]`;
    const offset = i * 8 - fadeDuration * i; // 8s clips with overlap

    filterParts.push(
      `${lastLabel}[${i}:v]xfade=transition=fade:duration=${fadeDuration}:offset=${offset.toFixed(2)}${outLabel}`
    );
    lastLabel = outLabel;
  }

  // Build input list
  const inputs = clipPaths.map((p) => `-i "${p}"`).join(" ");

  // Audio mixing: voice at full volume, music at 15%
  const audioFilter = `[${clipPaths.length}:a]volume=1.0[voice];[${clipPaths.length + 1}:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=longest[outa]`;

  const fullFilter = `${filterParts.join(";")};${audioFilter}`;

  const cmd = `ffmpeg -y ${inputs} -i "${voiceoverPath}" -i "${musicPath}" -filter_complex "${fullFilter}" -map "[outv]" -map "[outa]" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -shortest "${outputPath}" 2>&1`;

  execSync(cmd, { cwd: dir, maxBuffer: 50 * 1024 * 1024 });

  return outputPath;
}

export async function stitchAllVideos(
  videosData: {
    videoNumber: number;
    clipPaths: string[];
    voiceoverPath: string;
    musicPath: string;
  }[],
  outputDir: string,
  onProgress?: (videoNumber: number) => void
): Promise<string[]> {
  const outputs: string[] = [];

  for (const video of videosData) {
    const outputPath = path.join(outputDir, `video_${video.videoNumber}_final.mp4`);
    await stitchVideo({
      clipPaths: video.clipPaths,
      voiceoverPath: video.voiceoverPath,
      musicPath: video.musicPath,
      outputPath,
    });
    outputs.push(outputPath);
    onProgress?.(video.videoNumber);
  }

  return outputs;
}
