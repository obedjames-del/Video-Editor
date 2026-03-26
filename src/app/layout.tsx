import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sermon Video Generator — GrammarOfGrace",
  description:
    "Upload sermon slides and generate professional teaching videos with AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-gray-900 antialiased">
        <header className="border-b border-gray-100 px-6 py-4">
          <div className="mx-auto flex max-w-5xl items-center justify-between">
            <h1 className="text-lg font-semibold tracking-tight">
              GrammarOfGrace
            </h1>
            <span className="text-sm text-gray-400">
              Sermon Video Generator
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
