import { validateVeoPrompt, CLOSING_TAG } from "../framework/creative-director";
import { callClaude } from "./claude-client";
import { Scene } from "./storyboard-generator";

export interface SceneValidation {
  sceneNumber: number;
  valid: boolean;
  passed: string[];
  failed: string[];
}

export function validateScene(scene: Scene): SceneValidation {
  const result = validateVeoPrompt(scene.veoPrompt);
  return {
    sceneNumber: scene.sceneNumber,
    ...result,
  };
}

export function validateAllScenes(scenes: Scene[]): {
  allValid: boolean;
  results: SceneValidation[];
} {
  const results = scenes.map(validateScene);
  const allValid = results.every((r) => r.valid);
  return { allValid, results };
}

export async function autoFixPrompt(
  scene: Scene,
  failedCheckpoints: string[]
): Promise<string> {
  const systemPrompt = `You are a Veo prompt editor. Fix the given prompt so it passes ALL 6 Technical Accuracy Checkpoints. Only return the fixed prompt text, nothing else.

The prompt is missing these checkpoints:
${failedCheckpoints.map((f) => `- ${f}`).join("\n")}

Requirements:
- Skin tone must be explicitly named (e.g., "warm deep brown skin", "rich melanated complexion")
- Expression must be named (e.g., "contemplative gaze", "serene expression", "resolute look")
- Clothing materials and colors must be named (e.g., "undyed linen tunic", "dark wool suit")
- Background must have specific architecture/environment (e.g., "mudbrick walls", "stone temple interior")
- Lighting direction and quality must be stated (e.g., "warm golden light from the left", "soft ambient dawn light")
- Must end with: "${CLOSING_TAG}"`;

  return callClaude(systemPrompt, `Fix this Veo prompt:\n\n${scene.veoPrompt}`, 2048);
}
