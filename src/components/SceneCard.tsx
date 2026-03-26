"use client";

import { useState } from "react";
import { Scene } from "@/lib/ai/storyboard-generator";
import { validateVeoPrompt, ValidationResult } from "@/lib/framework/creative-director";

interface SceneCardProps {
  scene: Scene;
  onUpdate: (updated: Scene) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  isFirst: boolean;
  isLast: boolean;
}

export default function SceneCard({
  scene,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
}: SceneCardProps) {
  const [editing, setEditing] = useState(false);
  const [promptText, setPromptText] = useState(scene.veoPrompt);
  const validation: ValidationResult = validateVeoPrompt(scene.veoPrompt);

  const handleSave = () => {
    onUpdate({ ...scene, veoPrompt: promptText });
    setEditing(false);
  };

  const handleCancel = () => {
    setPromptText(scene.veoPrompt);
    setEditing(false);
  };

  return (
    <div
      className={`rounded-xl border p-4 ${
        validation.valid ? "border-gray-200" : "border-amber-300 bg-amber-50"
      }`}
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-700">
            Scene {scene.sceneNumber}
          </span>
          <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
            {scene.duration}s
          </span>
          <span className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600">
            {scene.era}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onMoveUp}
            disabled={isFirst}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30"
            title="Move up"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          </button>
          <button
            onClick={onMoveDown}
            disabled={isLast}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30"
            title="Move down"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <button
            onClick={onRemove}
            className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-500"
            title="Remove scene"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <p className="mb-2 text-sm text-gray-500">{scene.description}</p>

      {editing ? (
        <div className="flex flex-col gap-2">
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            rows={6}
            className="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="rounded-lg bg-gray-900 px-4 py-1.5 text-xs font-medium text-white hover:bg-gray-800"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="rounded-lg border border-gray-300 px-4 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div
          onClick={() => setEditing(true)}
          className="cursor-pointer rounded-lg bg-gray-50 p-3 text-xs leading-relaxed text-gray-600 hover:bg-gray-100"
        >
          {scene.veoPrompt}
        </div>
      )}

      {/* Validation badges */}
      <div className="mt-3 flex flex-wrap gap-1">
        {validation.passed.map((label) => (
          <span key={label} className="rounded-full bg-green-50 px-2 py-0.5 text-[10px] text-green-600">
            {label}
          </span>
        ))}
        {validation.failed.map((label) => (
          <span key={label} className="rounded-full bg-red-50 px-2 py-0.5 text-[10px] text-red-600">
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
