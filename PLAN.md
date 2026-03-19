# PowerPoint-to-Sermon-Video Generator — Implementation Plan

**Project**: Zoe Ministries / GrammarOfGrace Video Production Tool
**Last Updated**: 2026-03-19

---

## 1. Product Overview

A web application that accepts PowerPoint uploads (sermon slides) and generates **3 short sermon teaching videos** (~1-2 minutes each). The app intelligently splits slide content into groups, generates narration scripts, creates AI-powered illustrative video clips, and stitches everything together with voiceover, context-dependent background music, and dissolve transitions.

**Target Audience**: Faith-based / ministry use (personal/ministry tool)
**Auth**: None required — open access

---

## 2. Processing Pipeline

```
┌─────────────┐
│  1. UPLOAD   │  User uploads .pptx, .ppt, .pdf, or Google Slides
└──────┬──────┘
       ▼
┌─────────────────┐
│  2. EXTRACTION   │  Parse slides → extract text content from each slide
└──────┬──────────┘
       ▼
┌──────────────────────┐
│  3. SCRIPT GENERATION │  Claude API reads all slide text, flexibly splits
│     (Claude API)      │  into ~3 groups, and expands each group into a
│                       │  natural, flowing sermon-style narration script
└──────┬───────────────┘
       ▼
┌───────────────────────────┐
│  4. STORYBOARD GENERATION  │  Claude API analyzes each script, auto-detects
│     (Claude API)           │  era (Biblical / Historical / Contemporary),
│                            │  and generates Veo scene prompts using the
│                            │  Creative Director Framework. Each scene = 8s clip.
│                            │  ~8-15 clips per video.
└──────┬────────────────────┘
       ▼
┌────────────────────────┐
│  5. STORYBOARD REVIEW   │  User sees full storyboard with scene descriptions
│     (User Approval)     │  and Veo prompts. Can edit individual scene prompts,
│                         │  reorder, add, or remove clips before proceeding.
└──────┬─────────────────┘
       ▼
┌──────────────────────┐
│  6. PROMPT VALIDATION │  Strict validation: every Veo prompt must contain
│                       │  all 6 Technical Accuracy Checkpoints:
│                       │  ✓ Skin tone explicitly named
│                       │  ✓ Expression specified by name
│                       │  ✓ Clothing materials and colors named
│                       │  ✓ Background grounded (specific architecture/env)
│                       │  ✓ Lighting direction and quality stated
│                       │  ✓ Standard closing tag appended
│                       │  → BLOCKS generation if any checkpoint is missing
└──────┬───────────────┘
       ▼
┌─────────────────────────────────────────────┐
│  7. PARALLEL GENERATION                      │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Gemini Veo    │  │ ElevenLabs           │ │
│  │ Video Clips   │  │ Voiceover (Adam Stone)│ │
│  │ (8s each)     │  │ + Background Music   │ │
│  │ 1080p landscape│ │ (context-dependent)  │ │
│  └──────┬───────┘  └──────┬───────────────┘ │
│         │                  │                  │
└─────────┼──────────────────┼──────────────────┘
          ▼                  ▼
┌──────────────────────────┐
│  8. AUTOMATED QA          │  Vision AI reviews generated clip frames for:
│     (Gemini Vision)       │  • Hand/anatomy distortion
│                           │  • Skin tone accuracy
│                           │  • Anachronistic elements
│                           │  • Floating/disconnected elements
│                           │  • Over-stylized appearance
│                           │  → Flags or auto-regenerates failed clips
└──────┬───────────────────┘
       ▼
┌─────────────────────────┐
│  9. VIDEO STITCHING       │  FFmpeg combines:
│     (FFmpeg)              │  • Veo clips with dissolve transitions
│                           │  • Voiceover audio track
│                           │  • Background music (mixed lower than voice)
│                           │  Output: 3 × MP4 files, 1080p landscape
└──────┬────────────────────┘
       ▼
┌─────────────────┐
│  10. DELIVERY    │  3 MP4 files available for direct download
│                  │  Stored temporarily in Google Cloud Storage
└─────────────────┘
```

---

## 3. Creative Director & Historical Accuracy Framework

**Hardcoded into the application** — governs all Veo prompt generation.

### Era Categories (Auto-Detected by Claude from Script Content)

#### Biblical / Ancient Middle Eastern
- **Attire**: Undyed linen tunics (chiton/kethoneth), wool outer garments in earth tones (terracotta, ochre, deep brown, muted blue). No synthetic fabric, no modern silhouettes. Sandals: simple leather or woven reed.
- **Architecture**: Mudbrick, flat roofs, stone thresholds, oil lamp niches. Second Temple period references for 1st-century scenes. No Roman-era props in pre-Roman scenes.
- **Skin tones**: Explicit — warm deep brown / dark brown / rich melanated.
- **Expressions**: Composed authority, contemplation, reverence. Not suffering unless narrative demands it with dignity preserved.
- **Avoid**: Eurocentric facial features, anachronistic styles, overcrowded compositions.

#### Historical Period Pieces (Post-Biblical)
- **Era specificity**: Exact decade and region required — never generic "1800s."
- **Source material**: Documented period photography/illustration (Reconstruction-era portraits, Harlem Renaissance, Great Migration aesthetic).
- **Environments**: Period-accurate architecture, correct window glass, era-accurate signage, regional accuracy (Northern urban vs. Southern rural).
- **Expressions**: Dignity-first — strength, resolve, joy, intelligence as default. No perpetual-suffering coding.

#### Contemporary Scenes
- **Settings**: Specific environmental cues — time of day, light source, interior/exterior, surface materials. No stock-photo energy.
- **Wardrobe**: Character-specific. Ministerial: dark suit, clerical collar, or robe. Specify cut, color, context.

### 6 Technical Accuracy Checkpoints (Strict Validation)
1. Skin tone explicitly named
2. Expression specified by name
3. Clothing materials and colors named
4. Background grounded with specific architectural/environmental elements
5. Lighting direction and quality stated
6. Standard closing tag: "Photorealistic, no distortion, no hallucination, anatomically accurate hands, natural human proportions."

### Veo Prompt Template
```
[Subject description with explicit skin tone and expression]
[Exact attire with fabric, color, and period details]
[Specific environment with architectural/environmental grounding]
[Lighting: direction, quality, color temperature]
[Camera/composition guidance if needed]
Photorealistic, no distortion, no hallucination, anatomically accurate hands, natural human proportions.
```

### Common Visual Errors — Auto-QA Checklist
| Error | Correction |
|-------|-----------|
| Defaulting to lighter skin tones | Specify skin tone explicitly |
| Extra/fused fingers | "Anatomically accurate hands" in every prompt |
| Floating/disconnected elements | Specify subject anchoring |
| Over-stylized/painterly look | "Photorealistic" + "documentary-quality lighting" |
| Distress as default expression | Name a specific dignified expression |
| Anachronistic background elements | Name exact period, exclude modern elements |
| Generic "African" appearance | Specify region, era, and cultural context |

---

## 4. Tech Stack

### Frontend
- **Framework**: Next.js (React-based)
- **UI Style**: Clean & minimal — white/light background, simple upload area, modern
- **Key Pages**:
  - Upload page (drag & drop PowerPoint)
  - Script review page (3 scripts displayed for review)
  - Storyboard editor (scene-by-scene Veo prompt editor with reorder/add/remove)
  - Progress page (step-by-step progress bar during generation)
  - Download page (3 MP4 download buttons)

### Backend
- **Runtime**: Node.js (Next.js API routes) + Python microservice for FFmpeg processing
- **PowerPoint Parsing**: `python-pptx` (Python) for .pptx; `pdf-parse` for PDF; LibreOffice headless for .ppt conversion
- **Video Stitching**: FFmpeg (server-side)
  - Dissolve transitions between clips
  - Audio mixing (voiceover primary, music secondary)
  - Output: 1920x1080 MP4, H.264

### AI Services
| Service | Purpose | Details |
|---------|---------|---------|
| **Claude API** (Anthropic) | Script generation, storyboard creation, era detection, Veo prompt writing | Text intelligence layer |
| **Gemini Veo** (Google) | 8-second video clip generation | Illustrative biblical/sermon scenes |
| **Gemini Vision** (Google) | Automated QA on generated clips | Frame analysis for errors |
| **ElevenLabs** | Voiceover narration | Voice: **Adam Stone**, pastoral/warm tone |
| **ElevenLabs** | Background music generation | Context-dependent style (piano, pads, worship) based on sermon content |

### Storage & Hosting
- **Temp Storage**: Google Cloud Storage (auto-cleanup after download or 24h)
- **Hosting**: Google Cloud Run (containerized, scales to zero, handles long-running video jobs)
- **No database needed** (no auth, no persistent user data)

---

## 5. Supported Input Formats

| Format | Parser | Notes |
|--------|--------|-------|
| .pptx | `python-pptx` | Native parsing, best support |
| .ppt (legacy) | LibreOffice headless → .pptx | Convert first, then parse |
| .pdf | `pdf-parse` / `pdfplumber` | Extract text per page; each page = 1 "slide" |
| Google Slides | Google Slides API (export as .pptx) | User provides shareable link |

---

## 6. User Flow

```
1. Landing Page
   → Clean upload area: "Upload your sermon slides"
   → Supported formats shown: .pptx, .ppt, .pdf, Google Slides link
   → No login required

2. Upload & Processing
   → File uploads to server
   → Progress: "Extracting slide content..."
   → Slides parsed, text extracted

3. Script Review
   → 3 scripts displayed side by side
   → Each script shows which slides it covers
   → User can read, but scripts are auto-approved (view only? or editable?)
   → "Generate Storyboard" button

4. Storyboard Review & Edit
   → Each of the 3 videos shown as a timeline of scenes
   → Each scene card shows:
     - Scene number & duration (8s)
     - Era tag (Biblical / Historical / Contemporary)
     - Full Veo prompt text (editable)
     - Validation status (✓ all 6 checkpoints passed)
   → User can: edit prompts, reorder scenes, add/remove scenes
   → "Generate Videos" button (blocked if any prompt fails validation)

5. Video Generation (Progress Bar)
   → Step-by-step progress:
     ✓ Generating voiceover...
     ✓ Generating background music...
     ✓ Generating video clip 1/12...
     ✓ Generating video clip 2/12...
     ...
     ✓ Running quality check...
     ✓ Stitching Video 1...
     ✓ Stitching Video 2...
     ✓ Stitching Video 3...

6. Download Page
   → 3 video thumbnails with play preview
   → "Download MP4" button for each
   → "Download All" option
```

---

## 7. API Cost Estimates (Per Upload)

| Service | Usage | Est. Cost |
|---------|-------|-----------|
| Claude API | ~3 script generations + storyboard + validation | ~$0.50-1.00 |
| Gemini Veo | ~30-45 clips (8s each) across 3 videos | ~$3.00-8.00 |
| Gemini Vision | QA review of ~30-45 frames | ~$0.10-0.30 |
| ElevenLabs Voice | ~3-6 min total narration | ~$0.30-0.60 |
| ElevenLabs Music | 3 background tracks | ~$0.50-1.00 |
| GCS Storage | Temp storage ~500MB | ~$0.01 |
| **Total per upload** | | **~$4.50-11.00** |

*Note: Costs will vary based on actual API pricing and usage. To be revisited later.*

---

## 8. Project Structure (Proposed)

```
video-editor/
├── app/                          # Next.js app directory
│   ├── page.tsx                  # Landing / upload page
│   ├── scripts/page.tsx          # Script review page
│   ├── storyboard/page.tsx       # Storyboard editor page
│   ├── progress/page.tsx         # Generation progress page
│   ├── download/page.tsx         # Download page
│   ├── api/
│   │   ├── upload/route.ts       # Handle file upload
│   │   ├── extract/route.ts      # Extract slide content
│   │   ├── scripts/route.ts      # Generate scripts via Claude
│   │   ├── storyboard/route.ts   # Generate storyboard via Claude
│   │   ├── validate/route.ts     # Validate Veo prompts
│   │   ├── generate/route.ts     # Trigger video generation pipeline
│   │   └── status/route.ts       # Poll generation progress
│   └── layout.tsx
├── lib/
│   ├── parsers/
│   │   ├── pptx-parser.ts        # .pptx parsing
│   │   ├── pdf-parser.ts         # PDF parsing
│   │   └── slides-parser.ts      # Google Slides import
│   ├── ai/
│   │   ├── claude-client.ts      # Claude API client
│   │   ├── script-generator.ts   # Script generation logic
│   │   ├── storyboard-generator.ts # Storyboard + Veo prompt generation
│   │   └── prompt-validator.ts   # 6-checkpoint validation
│   ├── video/
│   │   ├── veo-client.ts         # Gemini Veo API client
│   │   ├── vision-qa.ts          # Gemini Vision QA checker
│   │   ├── elevenlabs-client.ts  # ElevenLabs voice + music client
│   │   └── ffmpeg-stitcher.ts    # FFmpeg video stitching
│   ├── storage/
│   │   └── gcs-client.ts         # Google Cloud Storage client
│   └── framework/
│       └── creative-director.ts  # Hardcoded Creative Director Framework
├── components/
│   ├── UploadZone.tsx
│   ├── ScriptViewer.tsx
│   ├── StoryboardEditor.tsx
│   ├── SceneCard.tsx
│   ├── ProgressTracker.tsx
│   └── VideoDownloader.tsx
├── public/
├── package.json
├── next.config.js
├── Dockerfile                    # For Cloud Run deployment
└── PLAN.md                       # This file
```

---

## 9. Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend | Next.js | Full-stack, API routes built in, easy deployment |
| Script/Storyboard AI | Claude API | Best for nuanced creative writing and prompt generation |
| Video Generation | Gemini Veo | 8s clip generation, illustrative scenes |
| QA Review | Gemini Vision | Best available for frame-by-frame visual QA |
| Voice | ElevenLabs (Adam Stone) | Fixed pastoral voice, high quality TTS |
| Music | ElevenLabs | Context-dependent generation, integrated with voice pipeline |
| Stitching | FFmpeg | Free, reliable, handles dissolves + audio mixing |
| Storage | Google Cloud Storage | Integrates with Google ecosystem (Veo, Cloud Run) |
| Hosting | Google Cloud Run | Handles long-running jobs, scales to zero |
| Auth | None | Personal/ministry tool, no need for user accounts |
| Creative Framework | Hardcoded | Won't change often, simpler than config management |

---

## 10. Implementation Phases

### Phase 1: Foundation
- [ ] Project setup (Next.js, dependencies)
- [ ] File upload UI + PowerPoint/PDF parsing
- [ ] Claude API integration for script generation
- [ ] Script review page

### Phase 2: Storyboard
- [ ] Claude-powered storyboard generation with era detection
- [ ] Creative Director Framework hardcoded
- [ ] 6-checkpoint prompt validation
- [ ] Storyboard editor UI (edit, reorder, add/remove scenes)

### Phase 3: Video Generation
- [ ] Gemini Veo integration (8s clip generation)
- [ ] ElevenLabs voice integration (Adam Stone)
- [ ] ElevenLabs music generation (context-dependent)
- [ ] Gemini Vision QA pipeline
- [ ] Progress tracking UI with real-time updates

### Phase 4: Stitching & Delivery
- [ ] FFmpeg stitching pipeline (dissolves, audio mixing)
- [ ] Google Cloud Storage integration
- [ ] Download page with MP4 delivery
- [ ] End-to-end testing

### Phase 5: Polish & Deploy
- [ ] Error handling and retry logic
- [ ] Google Cloud Run deployment (Dockerfile)
- [ ] Google Slides link import
- [ ] Legacy .ppt support via LibreOffice
- [ ] Performance optimization

---

*Plan created: 2026-03-19 | Zoe Ministries / GrammarOfGrace*
