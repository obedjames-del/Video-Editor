"use client";

interface VideoDownloaderProps {
  videoUrls: string[];
}

export default function VideoDownloader({ videoUrls }: VideoDownloaderProps) {
  return (
    <div className="flex flex-col gap-8">
      <div className="text-center">
        <h2 className="mb-2 text-2xl font-bold">Your Videos Are Ready!</h2>
        <p className="text-sm text-gray-500">
          {videoUrls.length} sermon teaching videos generated
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {videoUrls.map((url, i) => (
          <div
            key={i}
            className="flex flex-col items-center gap-4 rounded-xl border border-gray-200 bg-white p-6"
          >
            <div className="flex h-32 w-full items-center justify-center rounded-lg bg-gray-100">
              <video
                src={url}
                className="h-full w-full rounded-lg object-cover"
                controls
                preload="metadata"
              />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium">Video {i + 1}</p>
            </div>
            <a
              href={url}
              download={`sermon_video_${i + 1}.mp4`}
              className="w-full rounded-lg bg-gray-900 px-4 py-2.5 text-center text-sm font-medium text-white hover:bg-gray-800"
            >
              Download MP4
            </a>
          </div>
        ))}
      </div>

      {videoUrls.length > 1 && (
        <div className="flex justify-center">
          <button
            onClick={() => {
              videoUrls.forEach((url, i) => {
                const a = document.createElement("a");
                a.href = url;
                a.download = `sermon_video_${i + 1}.mp4`;
                a.click();
              });
            }}
            className="rounded-lg border border-gray-300 px-6 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Download All
          </button>
        </div>
      )}
    </div>
  );
}
