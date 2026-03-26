import { writeFile } from "fs/promises";
import path from "path";

const API_KEY = process.env.ELEVENLABS_API_KEY || "";
const ADAM_STONE_VOICE_ID = process.env.ELEVENLABS_VOICE_ID || "pNInz6obpgDQGcFmaJgB"; // Adam Stone

export interface VoiceoverResult {
  videoNumber: number;
  audioPath: string;
  success: boolean;
  error?: string;
}

export async function generateVoiceover(
  script: string,
  videoNumber: number,
  outputDir: string
): Promise<VoiceoverResult> {
  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${ADAM_STONE_VOICE_ID}`,
      {
        method: "POST",
        headers: {
          "xi-api-key": API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: script,
          model_id: "eleven_multilingual_v2",
          voice_settings: {
            stability: 0.6,
            similarity_boost: 0.75,
            style: 0.3,
            use_speaker_boost: true,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.status}`);
    }

    const audioBuffer = Buffer.from(await response.arrayBuffer());
    const audioPath = path.join(outputDir, `voiceover_${videoNumber}.mp3`);
    await writeFile(audioPath, audioBuffer);

    return { videoNumber, audioPath, success: true };
  } catch (err: unknown) {
    return {
      videoNumber,
      audioPath: "",
      success: false,
      error: err instanceof Error ? err.message : "Voiceover generation failed",
    };
  }
}

export interface MusicResult {
  videoNumber: number;
  musicPath: string;
  success: boolean;
  error?: string;
}

export async function generateBackgroundMusic(
  scriptSummary: string,
  videoNumber: number,
  durationSeconds: number,
  outputDir: string
): Promise<MusicResult> {
  try {
    // Determine music style from content
    const musicPrompt = `Gentle, contemplative ${
      scriptSummary.toLowerCase().includes("joy") ||
      scriptSummary.toLowerCase().includes("celebration")
        ? "worship piano and soft pads, uplifting"
        : "ambient piano, soft pads, meditative and warm"
    } background music for a sermon teaching video. ${durationSeconds} seconds.`;

    const response = await fetch(
      "https://api.elevenlabs.io/v1/text-to-sound-effects",
      {
        method: "POST",
        headers: {
          "xi-api-key": API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: musicPrompt,
          duration_seconds: durationSeconds,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`ElevenLabs Music API error: ${response.status}`);
    }

    const audioBuffer = Buffer.from(await response.arrayBuffer());
    const musicPath = path.join(outputDir, `music_${videoNumber}.mp3`);
    await writeFile(musicPath, audioBuffer);

    return { videoNumber, musicPath, success: true };
  } catch (err: unknown) {
    return {
      videoNumber,
      musicPath: "",
      success: false,
      error: err instanceof Error ? err.message : "Music generation failed",
    };
  }
}
