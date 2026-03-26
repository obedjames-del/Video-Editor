import { NextRequest, NextResponse } from "next/server";
import { readFile, writeFile } from "fs/promises";
import path from "path";
import { generateAllStoryboards } from "@/lib/ai/storyboard-generator";

export async function POST(req: NextRequest) {
  try {
    const { sessionId } = await req.json();
    if (!sessionId) {
      return NextResponse.json({ error: "Missing sessionId" }, { status: 400 });
    }

    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    const scripts = JSON.parse(
      await readFile(path.join(sessionDir, "scripts.json"), "utf-8")
    );

    const storyboards = await generateAllStoryboards(scripts);

    await writeFile(
      path.join(sessionDir, "storyboards.json"),
      JSON.stringify(storyboards, null, 2)
    );

    return NextResponse.json({ storyboards });
  } catch (err: unknown) {
    console.error("Storyboard generation error:", err);
    return NextResponse.json(
      { error: "Storyboard generation failed" },
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
    const storyboards = JSON.parse(
      await readFile(path.join(sessionDir, "storyboards.json"), "utf-8")
    );

    return NextResponse.json({ storyboards });
  } catch {
    return NextResponse.json(
      { error: "Storyboards not found" },
      { status: 404 }
    );
  }
}

export async function PUT(req: NextRequest) {
  try {
    const { sessionId, storyboards } = await req.json();
    if (!sessionId || !storyboards) {
      return NextResponse.json({ error: "Missing data" }, { status: 400 });
    }

    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    await writeFile(
      path.join(sessionDir, "storyboards.json"),
      JSON.stringify(storyboards, null, 2)
    );

    return NextResponse.json({ success: true });
  } catch (err: unknown) {
    console.error("Storyboard save error:", err);
    return NextResponse.json(
      { error: "Failed to save storyboards" },
      { status: 500 }
    );
  }
}
