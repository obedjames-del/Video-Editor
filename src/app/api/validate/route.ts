import { NextRequest, NextResponse } from "next/server";
import { validateAllScenes } from "@/lib/ai/prompt-validator";
import { Scene } from "@/lib/ai/storyboard-generator";

export async function POST(req: NextRequest) {
  try {
    const { scenes } = await req.json() as { scenes: Scene[] };
    if (!scenes || !Array.isArray(scenes)) {
      return NextResponse.json({ error: "Missing scenes" }, { status: 400 });
    }

    const validation = validateAllScenes(scenes);
    return NextResponse.json(validation);
  } catch (err: unknown) {
    console.error("Validation error:", err);
    return NextResponse.json(
      { error: "Validation failed" },
      { status: 500 }
    );
  }
}
