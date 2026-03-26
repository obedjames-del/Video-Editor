import JSZip from "jszip";
import { readFile } from "fs/promises";

interface SlideContent {
  slideNumber: number;
  text: string;
}

export async function parsePptx(filePath: string): Promise<SlideContent[]> {
  const data = await readFile(filePath);
  const zip = await JSZip.loadAsync(data);

  // Find all slide XML files
  const slideFiles: string[] = [];
  zip.forEach((relativePath) => {
    if (/^ppt\/slides\/slide\d+\.xml$/.test(relativePath)) {
      slideFiles.push(relativePath);
    }
  });

  // Sort by slide number
  slideFiles.sort((a, b) => {
    const numA = parseInt(a.match(/slide(\d+)/)?.[1] || "0");
    const numB = parseInt(b.match(/slide(\d+)/)?.[1] || "0");
    return numA - numB;
  });

  const slides: SlideContent[] = [];

  for (let i = 0; i < slideFiles.length; i++) {
    const xmlContent = await zip.file(slideFiles[i])?.async("string");
    if (!xmlContent) continue;

    // Extract text from XML by finding all <a:t> tags
    const textParts: string[] = [];
    const regex = /<a:t[^>]*>([\s\S]*?)<\/a:t>/g;
    let match;
    while ((match = regex.exec(xmlContent)) !== null) {
      const text = match[1].trim();
      if (text) textParts.push(text);
    }

    slides.push({
      slideNumber: i + 1,
      text: textParts.join(" "),
    });
  }

  return slides.filter((s) => s.text.length > 0);
}
