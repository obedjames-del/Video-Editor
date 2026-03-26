import { GoogleGenAI } from "@google/genai";
import { readFile } from "fs/promises";

const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface QAResult {
  sceneNumber: number;
  passed: boolean;
  issues: string[];
  severity: "pass" | "warning" | "fail";
}

const QA_PROMPT = `You are a visual QA inspector for AI-generated sermon video clips. Analyze this video frame for the following issues:

1. Hand/anatomy distortion — extra fingers, fused digits, unnaturally bent limbs
2. Skin tone accuracy — does the subject have the warm deep brown / dark brown / melanated skin tone expected?
3. Anachronistic elements — modern items in biblical/historical scenes
4. Floating/disconnected elements — objects not properly grounded
5. Over-stylized appearance — too painterly, not photorealistic enough

Respond with ONLY valid JSON:
{
  "passed": true/false,
  "issues": ["issue description 1", "issue description 2"],
  "severity": "pass" | "warning" | "fail"
}

If there are no issues, respond with {"passed": true, "issues": [], "severity": "pass"}`;

export async function qaCheckClip(
  videoPath: string,
  sceneNumber: number
): Promise<QAResult> {
  try {
    // Extract a frame from the video for analysis
    const { execSync } = await import("child_process");
    const framePath = videoPath.replace(".mp4", "_frame.jpg");

    execSync(
      `ffmpeg -i "${videoPath}" -ss 4 -vframes 1 -q:v 2 "${framePath}" -y 2>/dev/null`
    );

    const frameData = await readFile(framePath);
    const base64Frame = frameData.toString("base64");

    const response = await client.models.generateContent({
      model: "gemini-2.0-flash",
      contents: [
        {
          role: "user",
          parts: [
            { text: QA_PROMPT },
            {
              inlineData: {
                mimeType: "image/jpeg",
                data: base64Frame,
              },
            },
          ],
        },
      ],
    });

    const text = response.text || "";
    const jsonStr = text.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
    const result = JSON.parse(jsonStr);

    return { sceneNumber, ...result };
  } catch (err: unknown) {
    console.error(`QA check failed for scene ${sceneNumber}:`, err);
    return {
      sceneNumber,
      passed: true, // Don't block on QA failures
      issues: ["QA check could not be completed"],
      severity: "warning",
    };
  }
}

export async function qaCheckAllClips(
  clips: { sceneNumber: number; videoPath: string }[]
): Promise<QAResult[]> {
  const results: QAResult[] = [];

  for (const clip of clips) {
    const result = await qaCheckClip(clip.videoPath, clip.sceneNumber);
    results.push(result);
  }

  return results;
}
