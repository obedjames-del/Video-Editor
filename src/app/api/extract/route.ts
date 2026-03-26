import { NextRequest, NextResponse } from "next/server";
import { readFile, writeFile } from "fs/promises";
import path from "path";
import { parsePptx } from "@/lib/parsers/pptx-parser";
import { parsePdf } from "@/lib/parsers/pdf-parser";

export async function POST(req: NextRequest) {
  try {
    const { sessionId } = await req.json();
    if (!sessionId) {
      return NextResponse.json({ error: "Missing sessionId" }, { status: 400 });
    }

    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    const meta = JSON.parse(
      await readFile(path.join(sessionDir, "meta.json"), "utf-8")
    );

    let slides;
    if (meta.fileType === ".pptx") {
      slides = await parsePptx(meta.filePath);
    } else if (meta.fileType === ".pdf") {
      slides = await parsePdf(meta.filePath);
    } else {
      return NextResponse.json(
        { error: `Unsupported file type: ${meta.fileType}` },
        { status: 400 }
      );
    }

    // Save extracted slides
    await writeFile(
      path.join(sessionDir, "slides.json"),
      JSON.stringify(slides, null, 2)
    );

    return NextResponse.json({ slides, count: slides.length });
  } catch (err: unknown) {
    console.error("Extract error:", err);
    return NextResponse.json(
      { error: "Extraction failed" },
      { status: 500 }
    );
  }
}
