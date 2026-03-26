/**
 * Creative Director & Historical Accuracy Framework
 * Hardcoded into the application — governs all Veo prompt generation.
 */

export const ERA_CATEGORIES = {
  BIBLICAL: "Biblical / Ancient Middle Eastern",
  HISTORICAL: "Historical Period Piece",
  CONTEMPORARY: "Contemporary",
} as const;

export type EraCategory = (typeof ERA_CATEGORIES)[keyof typeof ERA_CATEGORIES];

export const ERA_GUIDELINES: Record<EraCategory, string> = {
  [ERA_CATEGORIES.BIBLICAL]: `
- Attire: Undyed linen tunics (chiton/kethoneth), wool outer garments in earth tones (terracotta, ochre, deep brown, muted blue). No synthetic fabric, no modern silhouettes. Sandals: simple leather or woven reed.
- Architecture: Mudbrick, flat roofs, stone thresholds, oil lamp niches. Second Temple period references for 1st-century scenes. No Roman-era props in pre-Roman scenes.
- Skin tones: Explicit — warm deep brown / dark brown / rich melanated.
- Expressions: Composed authority, contemplation, reverence. Not suffering unless narrative demands it with dignity preserved.
- Avoid: Eurocentric facial features, anachronistic styles, overcrowded compositions.`,

  [ERA_CATEGORIES.HISTORICAL]: `
- Era specificity: Exact decade and region required — never generic "1800s."
- Source material: Documented period photography/illustration (Reconstruction-era portraits, Harlem Renaissance, Great Migration aesthetic).
- Environments: Period-accurate architecture, correct window glass, era-accurate signage, regional accuracy (Northern urban vs. Southern rural).
- Expressions: Dignity-first — strength, resolve, joy, intelligence as default. No perpetual-suffering coding.`,

  [ERA_CATEGORIES.CONTEMPORARY]: `
- Settings: Specific environmental cues — time of day, light source, interior/exterior, surface materials. No stock-photo energy.
- Wardrobe: Character-specific. Ministerial: dark suit, clerical collar, or robe. Specify cut, color, context.`,
};

export const TECHNICAL_CHECKPOINTS = [
  { id: "skin_tone", label: "Skin tone explicitly named", pattern: /(?:skin|tone|melanated|brown|dark|complexion)/i },
  { id: "expression", label: "Expression specified by name", pattern: /(?:expression|gaze|look|contemplat|serene|resolute|joyful|composed|authoritative|reverent|dignified|thoughtful|warm|determined)/i },
  { id: "clothing", label: "Clothing materials and colors named", pattern: /(?:linen|wool|cotton|silk|tunic|robe|garment|suit|fabric|cloth|dress|wearing|clad|attire)/i },
  { id: "background", label: "Background grounded (specific architecture/env)", pattern: /(?:mudbrick|stone|temple|church|room|wall|building|street|landscape|interior|exterior|ceiling|floor|garden|courtyard|village)/i },
  { id: "lighting", label: "Lighting direction and quality stated", pattern: /(?:light|lit|glow|shadow|sun|lamp|warm light|soft light|golden|ambient|natural light|dramatic|dawn|dusk|candlelight)/i },
  { id: "closing_tag", label: "Standard closing tag appended", pattern: /photorealistic.*no distortion.*anatomically accurate hands/i },
] as const;

export const CLOSING_TAG =
  "Photorealistic, no distortion, no hallucination, anatomically accurate hands, natural human proportions.";

export const VEO_PROMPT_TEMPLATE = `[Subject description with explicit skin tone and expression]
[Exact attire with fabric, color, and period details]
[Specific environment with architectural/environmental grounding]
[Lighting: direction, quality, color temperature]
[Camera/composition guidance if needed]
${CLOSING_TAG}`;

export interface ValidationResult {
  valid: boolean;
  passed: string[];
  failed: string[];
}

export function validateVeoPrompt(prompt: string): ValidationResult {
  const passed: string[] = [];
  const failed: string[] = [];

  for (const checkpoint of TECHNICAL_CHECKPOINTS) {
    if (checkpoint.pattern.test(prompt)) {
      passed.push(checkpoint.label);
    } else {
      failed.push(checkpoint.label);
    }
  }

  return { valid: failed.length === 0, passed, failed };
}

export const COMMON_ERRORS = [
  { error: "Defaulting to lighter skin tones", correction: "Specify skin tone explicitly" },
  { error: "Extra/fused fingers", correction: '"Anatomically accurate hands" in every prompt' },
  { error: "Floating/disconnected elements", correction: "Specify subject anchoring" },
  { error: 'Over-stylized/painterly look', correction: '"Photorealistic" + "documentary-quality lighting"' },
  { error: "Distress as default expression", correction: "Name a specific dignified expression" },
  { error: "Anachronistic background elements", correction: "Name exact period, exclude modern elements" },
  { error: 'Generic "African" appearance', correction: "Specify region, era, and cultural context" },
];
