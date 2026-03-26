"use client";

import { useState } from "react";
import { Storyboard, Scene } from "@/lib/ai/storyboard-generator";
import { validateAllScenes } from "@/lib/ai/prompt-validator";
import { CLOSING_TAG } from "@/lib/framework/creative-director";
import SceneCard from "./SceneCard";

interface StoryboardEditorProps {
  storyboards: Storyboard[];
  onSave: (storyboards: Storyboard[]) => Promise<void>;
  onGenerate: () => void;
  generating?: boolean;
}

export default function StoryboardEditor({
  storyboards: initial,
  onSave,
  onGenerate,
  generating,
}: StoryboardEditorProps) {
  const [storyboards, setStoryboards] = useState<Storyboard[]>(initial);
  const [activeVideo, setActiveVideo] = useState(0);

  const currentBoard = storyboards[activeVideo];

  const allScenes = storyboards.flatMap((sb) => sb.scenes);
  const validation = validateAllScenes(allScenes);

  const updateScene = (sceneIndex: number, updated: Scene) => {
    const newBoards = [...storyboards];
    newBoards[activeVideo] = {
      ...newBoards[activeVideo],
      scenes: newBoards[activeVideo].scenes.map((s, i) =>
        i === sceneIndex ? updated : s
      ),
    };
    setStoryboards(newBoards);
  };

  const removeScene = (sceneIndex: number) => {
    const newBoards = [...storyboards];
    newBoards[activeVideo] = {
      ...newBoards[activeVideo],
      scenes: newBoards[activeVideo].scenes
        .filter((_, i) => i !== sceneIndex)
        .map((s, i) => ({ ...s, sceneNumber: i + 1 })),
    };
    setStoryboards(newBoards);
  };

  const moveScene = (sceneIndex: number, direction: -1 | 1) => {
    const newBoards = [...storyboards];
    const scenes = [...newBoards[activeVideo].scenes];
    const targetIndex = sceneIndex + direction;
    if (targetIndex < 0 || targetIndex >= scenes.length) return;
    [scenes[sceneIndex], scenes[targetIndex]] = [scenes[targetIndex], scenes[sceneIndex]];
    scenes.forEach((s, i) => (s.sceneNumber = i + 1));
    newBoards[activeVideo] = { ...newBoards[activeVideo], scenes };
    setStoryboards(newBoards);
  };

  const addScene = () => {
    const newBoards = [...storyboards];
    const scenes = newBoards[activeVideo].scenes;
    const newScene: Scene = {
      sceneNumber: scenes.length + 1,
      duration: 8,
      era: scenes[0]?.era || "Contemporary",
      description: "New scene — edit description",
      veoPrompt: `[Subject description with explicit skin tone and expression]\n[Exact attire with fabric, color, and period details]\n[Specific environment with architectural/environmental grounding]\n[Lighting: direction, quality, color temperature]\n${CLOSING_TAG}`,
    };
    newBoards[activeVideo] = {
      ...newBoards[activeVideo],
      scenes: [...scenes, newScene],
    };
    setStoryboards(newBoards);
  };

  const handleSaveAndGenerate = async () => {
    await onSave(storyboards);
    onGenerate();
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Storyboard Editor</h2>
        <div className="flex items-center gap-2">
          {validation.allValid ? (
            <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-600">
              All prompts valid
            </span>
          ) : (
            <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-600">
              {validation.results.filter((r) => !r.valid).length} prompts need fixes
            </span>
          )}
        </div>
      </div>

      {/* Video tabs */}
      <div className="flex gap-2">
        {storyboards.map((sb, i) => (
          <button
            key={sb.videoNumber}
            onClick={() => setActiveVideo(i)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              i === activeVideo
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Video {sb.videoNumber}: {sb.title}
          </button>
        ))}
      </div>

      {/* Scene list */}
      <div className="flex flex-col gap-4">
        {currentBoard.scenes.map((scene, i) => (
          <SceneCard
            key={`${activeVideo}-${scene.sceneNumber}`}
            scene={scene}
            onUpdate={(updated) => updateScene(i, updated)}
            onRemove={() => removeScene(i)}
            onMoveUp={() => moveScene(i, -1)}
            onMoveDown={() => moveScene(i, 1)}
            isFirst={i === 0}
            isLast={i === currentBoard.scenes.length - 1}
          />
        ))}
      </div>

      {/* Add scene button */}
      <button
        onClick={addScene}
        className="flex items-center justify-center gap-2 rounded-xl border-2 border-dashed border-gray-200 py-4 text-sm text-gray-400 hover:border-gray-300 hover:text-gray-500"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add Scene
      </button>

      {/* Generate button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={handleSaveAndGenerate}
          disabled={!validation.allValid || generating}
          className="rounded-lg bg-gray-900 px-8 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {!validation.allValid
            ? "Fix all prompts before generating"
            : generating
            ? "Starting generation..."
            : "Generate Videos"}
        </button>
      </div>
    </div>
  );
}
