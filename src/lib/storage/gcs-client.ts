import { Storage } from "@google-cloud/storage";
import { readFile } from "fs/promises";
import path from "path";

const BUCKET_NAME = process.env.GCS_BUCKET_NAME || "grammarofgrace-videos";

let storage: Storage;
function getStorage() {
  if (!storage) {
    storage = new Storage({
      projectId: process.env.GCP_PROJECT_ID,
      keyFilename: process.env.GCP_KEY_FILE,
    });
  }
  return storage;
}

export async function uploadToGCS(
  localPath: string,
  sessionId: string
): Promise<string> {
  const gcs = getStorage();
  const bucket = gcs.bucket(BUCKET_NAME);
  const fileName = `${sessionId}/${path.basename(localPath)}`;

  await bucket.upload(localPath, {
    destination: fileName,
    metadata: {
      contentType: "video/mp4",
      metadata: {
        sessionId,
        uploadedAt: new Date().toISOString(),
      },
    },
  });

  // Generate signed URL (valid for 24h)
  const [url] = await bucket.file(fileName).getSignedUrl({
    action: "read",
    expires: Date.now() + 24 * 60 * 60 * 1000,
  });

  return url;
}

export async function uploadAllVideos(
  videoPaths: string[],
  sessionId: string
): Promise<string[]> {
  const urls: string[] = [];
  for (const videoPath of videoPaths) {
    const url = await uploadToGCS(videoPath, sessionId);
    urls.push(url);
  }
  return urls;
}

export async function cleanupSession(sessionId: string): Promise<void> {
  try {
    const gcs = getStorage();
    const bucket = gcs.bucket(BUCKET_NAME);
    await bucket.deleteFiles({ prefix: `${sessionId}/` });
  } catch (err) {
    console.error("GCS cleanup error:", err);
  }
}
