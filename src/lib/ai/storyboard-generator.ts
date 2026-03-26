import { callClaude } from "./claude-client";
import { ERA_GUIDELINES, CLOSING_TAG, ERA_CATEGORIES } from "../framework/creative-director";
import { GeneratedScript } from "./script-generator";

export interface Scene {
  sceneNumber: number;
  duration: number;
  era: string;
  description: string;
  veoPrompt: string;
}

export interface Storyboard {
  videoNumber: number;
  title: string;
  scenes: Scene[];
}

const SYSTEM_PROMPT = `You are a Creative Director for GrammarOfGrace / Zoe Ministries sermon videos. Your job is to take a narration script and generate a visual storyboard of scenes, each with a detailed Veo video generation prompt.

CREATIVE DIRECTOR FRAMEWORK:

ERA CATEGORIES — auto-detect which applies to each scene:

${ERA_CATEGORIES.BIBLICAL}:
${ERA_GUIDELINES[ERA_CATEGORIES.BIBLICAL]}

${ERA_CATEGORIES.HISTORICAL}:
${ERA_GUIDELINES[ERA_CATEGORIES.HISTORICAL]}

${ERA_CATEGORIES.CONTEMPORARY}:
${ERA_GUIDELINES[ERA_CATEGORIES.CONTEMPORARY]}

RULES FOR VEO PROMPTS:
1. Each scene is an 8-second video clip at 1080p landscape.
2. Generate 8-15 scenes per video script.
3. Every Veo prompt MUST include ALL 6 Technical Accuracy Checkpoints:
   - Skin tone explicitly named
   - Expression specified by name
   - Clothing materials and colors named
   - Background grounded with specific architectural/environmental elements
   - Lighting direction and quality stated
   - End with: "${CLOSING_TAG}"
4. Auto-detect the era (Biblical, Historical, Contemporary) from script content.
5. Prompts must be visually rich, specific, and grounded — no vague or generic descriptions.
6. Scenes should illustrate the narration — they are visual accompaniment, not literal recreations.

OUTPUT FORMAT (respond with valid JSON only, no markdown):
{
  "videoNumber": 1,
  "title": "Video title",
  "scenes": [
    {
      "sceneNumber": 1,
      "duration": 8,
      "era": "Biblical / Ancient Middle Eastern",
      "description": "Brief description of what this scene shows",
      "veoPrompt": "Full detailed Veo prompt with all 6 checkpoints..."
    }
  ]
}`;

export async function generateStoryboard(
  script: GeneratedScript
): Promise<Storyboard> {
  const userMessage = `Generate a visual storyboard for this sermon video script:

Title: ${script.title}
Video Number: ${script.videoNumber}

Script:
${script.script}`;

  const response = await callClaude(SYSTEM_PROMPT, userMessage, 8192);

  const jsonStr = response.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
  return JSON.parse(jsonStr);
}

export async function generateAllStoryboards(
  scripts: GeneratedScript[]
): Promise<Storyboard[]> {
  const storyboards = await Promise.all(
    scripts.map((script) => generateStoryboard(script))
  );
  return storyboards;
}
