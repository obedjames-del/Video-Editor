import { callClaude } from "./claude-client";

interface SlideContent {
  slideNumber: number;
  text: string;
}

export interface GeneratedScript {
  videoNumber: number;
  title: string;
  slideRange: string;
  script: string;
}

const SYSTEM_PROMPT = `You are a sermon script writer for GrammarOfGrace / Zoe Ministries. Your job is to take slide content from a PowerPoint sermon and transform it into natural, flowing narration scripts for short teaching videos.

RULES:
1. Split the slides into exactly 3 groups. Each group becomes one video script (~1-2 minutes when spoken).
2. The split should be natural and thematic — group related content together.
3. Each script should flow naturally as spoken narration. Don't reference slides directly.
4. Maintain the theological content and teaching points faithfully.
5. Use a warm, pastoral, authoritative tone — like a seasoned teacher explaining to an engaged audience.
6. Each script should have a clear opening hook, teaching body, and closing thought.
7. Do NOT add content that isn't in the slides — expand and make it flow, but stay faithful to the source.

OUTPUT FORMAT (respond with valid JSON only, no markdown):
[
  {
    "videoNumber": 1,
    "title": "Short descriptive title",
    "slideRange": "Slides 1-5",
    "script": "The full narration script text..."
  },
  {
    "videoNumber": 2,
    "title": "Short descriptive title",
    "slideRange": "Slides 6-10",
    "script": "The full narration script text..."
  },
  {
    "videoNumber": 3,
    "title": "Short descriptive title",
    "slideRange": "Slides 11-15",
    "script": "The full narration script text..."
  }
]`;

export async function generateScripts(
  slides: SlideContent[]
): Promise<GeneratedScript[]> {
  const slideText = slides
    .map((s) => `--- Slide ${s.slideNumber} ---\n${s.text}`)
    .join("\n\n");

  const userMessage = `Here are the slide contents from a sermon PowerPoint. Please split them into 3 groups and generate narration scripts for 3 short teaching videos.\n\n${slideText}`;

  const response = await callClaude(SYSTEM_PROMPT, userMessage, 8192);

  // Parse JSON from response — handle potential markdown wrapping
  const jsonStr = response.replace(/```json?\n?/g, "").replace(/```/g, "").trim();
  return JSON.parse(jsonStr);
}
