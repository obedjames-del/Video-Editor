import { NextRequest, NextResponse } from "next/server";
import { writeFile, mkdir } from "fs/promises";
import path from "path";
import { v4 as uuidv4 } from "uuid";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
    }

    const ext = path.extname(file.name).toLowerCase();
    if (![".pptx", ".ppt", ".pdf"].includes(ext)) {
      return NextResponse.json(
        { error: "Unsupported file type. Please upload .pptx, .ppt, or .pdf" },
        { status: 400 }
      );
    }

    const sessionId = uuidv4();
    const sessionDir = path.join(process.cwd(), "tmp", sessionId);
    await mkdir(sessionDir, { recursive: true });

    const buffer = Buffer.from(await file.arrayBuffer());
    const filePath = path.join(sessionDir, `upload${ext}`);
    await writeFile(filePath, buffer);

    // Write session metadata
    const meta = {
      sessionId,
      originalName: file.name,
      fileType: ext,
      filePath,
      uploadedAt: new Date().toISOString(),
    };
    await writeFile(
      path.join(sessionDir, "meta.json"),
      JSON.stringify(meta, null, 2)
    );

    return NextResponse.json({ sessionId });
  } catch (err: unknown) {
    console.error("Upload error:", err);
    return NextResponse.json(
      { error: "Upload failed" },
      { status: 500 }
    );
  }
}
