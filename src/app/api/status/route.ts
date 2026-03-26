import { NextRequest, NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("session");
  if (!sessionId) {
    return NextResponse.json({ error: "Missing session" }, { status: 400 });
  }

  try {
    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    const progress = JSON.parse(
      await readFile(path.join(sessionDir, "progress.json"), "utf-8")
    );
    return NextResponse.json(progress);
  } catch {
    return NextResponse.json({
      stage: "waiting",
      detail: "Waiting to start...",
      completed: 0,
      total: 0,
    });
  }
}
