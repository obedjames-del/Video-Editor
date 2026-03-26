import { readFile } from "fs/promises";

interface SlideContent {
  slideNumber: number;
  text: string;
}

export async function parsePdf(filePath: string): Promise<SlideContent[]> {
  const buffer = await readFile(filePath);
  // Use dynamic import to handle pdf-parse's module format
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { PDFParse } = require("pdf-parse");
  const parser = new PDFParse(buffer);
  const data = await parser.loadPDF(buffer);

  // Split by page breaks — pdf-parse separates pages with form feeds
  const fullText: string = data.text || "";
  const pages = fullText.split(/\f/).filter((p: string) => p.trim().length > 0);

  return pages.map((text: string, i: number) => ({
    slideNumber: i + 1,
    text: text.trim(),
  }));
}
