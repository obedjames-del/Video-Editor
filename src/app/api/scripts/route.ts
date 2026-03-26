import { NextRequest, NextResponse } from "next/server";
import { readFile, writeFile } from "fs/promises";
import path from "path";
import { generateScripts } from "@/lib/ai/script-generator";

export async function POST(req: NextRequest) {
  try {
    const { sessionId } = await req.json();
    if (!sessionId) {
      return NextResponse.json({ error: "Missing sessionId" }, { status: 400 });
    }

    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    const slides = JSON.parse(
      await readFile(path.join(sessionDir, "slides.json"), "utf-8")
    );

    const scripts = await generateScripts(slides);

    await writeFile(
      path.join(sessionDir, "scripts.json"),
      JSON.stringify(scripts, null, 2)
    );

    return NextResponse.json({ scripts });
  } catch (err: unknown) {
    console.error("Script generation error:", err);
    return NextResponse.json(
      { error: "Script generation failed" },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const sessionId = req.nextUrl.searchParams.get("session");
    if (!sessionId) {
      return NextResponse.json({ error: "Missing session" }, { status: 400 });
    }

    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    const scripts = JSON.parse(
      await readFile(path.join(sessionDir, "scripts.json"), "utf-8")
    );

    return NextResponse.json({ scripts });
  } catch {
    return NextResponse.json(
      { error: "Scripts not found" },
      { status: 404 }
    );
  }
}
