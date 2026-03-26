import { GoogleGenAI } from "@google/genai";

const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface VeoGenerationResult {
  sceneNumber: number;
  videoPath: string;
  success: boolean;
  error?: string;
}

export async function generateVideoClip(
  prompt: string,
  sceneNumber: number,
  outputDir: string
): Promise<VeoGenerationResult> {
  try {
    // Use Gemini's video generation (Veo)
    const operation = await client.models.generateVideos({
      model: "veo-2.0-generate-001",
      prompt,
      config: {
        aspectRatio: "16:9",
        numberOfVideos: 1,
        durationSeconds: 8,
      },
    });

    // Poll for completion
    let result = operation;
    while (!result.done) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      result = await client.operations.get({ operation: result as any });
    }

    // Download the generated video
    if (result.response?.generatedVideos?.[0]?.video?.uri) {
      const videoUri = result.response.generatedVideos[0].video.uri;
      const { writeFile } = await import("fs/promises");
      const path = await import("path");

      const videoPath = path.join(outputDir, `scene_${sceneNumber}.mp4`);

      // Fetch and save the video
      const response = await fetch(videoUri);
      const buffer = Buffer.from(await response.arrayBuffer());
      await writeFile(videoPath, buffer);

      return { sceneNumber, videoPath, success: true };
    }

    return {
      sceneNumber,
      videoPath: "",
      success: false,
      error: "No video generated",
    };
  } catch (err: unknown) {
    return {
      sceneNumber,
      videoPath: "",
      success: false,
      error: err instanceof Error ? err.message : "Video generation failed",
    };
  }
}

export async function generateAllClips(
  scenes: { sceneNumber: number; veoPrompt: string }[],
  outputDir: string,
  onProgress?: (completed: number, total: number) => void
): Promise<VeoGenerationResult[]> {
  const results: VeoGenerationResult[] = [];

  // Generate clips sequentially to avoid rate limits
  for (let i = 0; i < scenes.length; i++) {
    const scene = scenes[i];
    const result = await generateVideoClip(
      scene.veoPrompt,
      scene.sceneNumber,
      outputDir
    );
    results.push(result);
    onProgress?.(i + 1, scenes.length);
  }

  return results;
}
