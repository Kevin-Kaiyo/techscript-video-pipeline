# Project Audit - 2026-05-18

This audit captures the handoff state after the first public release of TechScript Video Pipeline.
The project is useful as a working prototype, but it is not yet a clean reusable product.

Update after Phase A/B stabilization: the legacy EP01 scripts have been archived, current-status docs have been rewritten, `package.json` and `pipeline/preflight.mjs` have been added, and the TTS path assumption has been fixed. The remaining major product gap is Phase C: a real Manim demo.

## Current Verdict

TechScript Video Pipeline currently mixes three layers:

1. A real local production workflow that can render HyperFrames videos.
2. Legacy Micro LED EP01 experiment code and documents.
3. New product ambitions: reusable technical video pipeline, Manim templates, TTS provider abstraction, and future LLM script generation.

The main risk is not one broken script. The main risk is unclear product boundaries: readers cannot yet tell which files are stable API, which are demos, and which are historical artifacts.

## What Is Solid

- HyperFrames browser-render path exists and is documented: index.html -> Chrome CDP screenshots -> FFmpeg silent MP4 -> audio mix.
- TTS provider abstraction exists under pipeline/tts/, with Edge TTS as the practical default.
- Generated media and personal voice samples are ignored by git.
- Public repository no longer tracks large MP3/WAV/MP4 artifacts.
- make check passes for local binary dependencies: ffmpeg, node, python3, Chrome, and bc.
- Python syntax checks and Node syntax checks pass for current pipeline scripts.

## Critical Problems

### 1. Product Architecture Is Not Yet Clean

The repo still contains product docs, historical planning docs, demo episodes, and legacy EP01 implementation in one level. For example:

- README.md describes the new TechScript Video Pipeline.
- PROJECT.md still describes an older Micro LED project flow using assets/, sag, and Remotion.
- STRUCTURE.md still references math_video_pipeline as a symlink dependency, even though the current public shape moved away from that.
- VIDEO_PIPELINE_PLAN.md contains useful history, but it is not a clean product roadmap.

Required fix: split docs into docs/status/, docs/roadmap/, and current user-facing docs. Archive or rewrite legacy plans.

### 2. The Build Path Assumes Local Generated Audio

pipeline/build_episode.sh mixes voiceover if audio_schedule.json exists, but the public repo does not include generated voice files.

That means a fresh clone can follow the README only if users generate audio first. This is acceptable, but the build script should fail with a clear message instead of reaching FFmpeg with missing inputs.

Required fix: add preflight validation for audio/voiceover/*.mp3, audio_schedule.json, Chrome, ffmpeg, node module ws, and writable temp paths.

### 3. No Root Dependency Manifest For Node

The renderer installs ws into /tmp/node_modules. This works on Kevin's machine, but it is not a reproducible open-source setup.

Required fix: add root package.json with scripts and dependencies, or vendor a small install script that clearly owns .cache/ or node_modules/.

### 4. Frame Rate Is Inconsistent

PROJECT.md says 30fps, while the active HyperFrames build defaults to 24fps.

Required fix: make shared/brand/video.json the single source of truth and have scripts read from it unless overridden by FPS=.

### 5. Manim Is Present But Not Productized

Manim files exist under pipeline/manim/, but the shipped technical demo still uses HyperFrames. README correctly labels Manim as planned, but the project promise depends on Manim for technical/algorithmic content.

Required fix: create one real demo-manim episode that renders through a documented command and outputs a video artifact locally.

## Important Problems

### 6. tts_cli.py Has A Hard-Coded Project Folder Assumption

tts_cli.py resolves episode paths through ROOT / techscript-video-pipeline/episodes / ep.
This works only when the checkout directory is exactly named techscript-video-pipeline and lives one level below ROOT.

Required fix: derive project root from Path(__file__).resolve().parents[1].

### 7. Legacy Scripts Still Target Old assets/ Structure

pipeline/render_video.py, pipeline/generate_scenes.py, and some old docs still refer to the previous static-image pipeline.

Required fix: either move legacy scripts into archive/legacy_ep01/ or update them to the current episodes/<ep>/ layout.

### 8. CI Is Missing From The Public Commit

.github/ exists locally but is ignored and contains no committed workflow. The repo has no automated smoke check.

Required fix: add a lightweight CI that runs:

- Python syntax check
- Node syntax check
- README link/path check
- make check equivalent where possible

### 9. Documentation Mentions A Missing CosyVoice Setup File

README.md, docs/SETUP.md, and docs/WORKFLOW.md reference docs/SETUP_COSYVOICE.md, but that file does not exist.

Required fix: add docs/SETUP_COSYVOICE.md or remove the reference until it is ready.

## Recommended Stabilization Order

### Phase A - Make The Repo Honest

- Rewrite PROJECT.md as current product status, not the old EP01 project.
- Rewrite STRUCTURE.md to match the actual repo.
- Add this audit to README or link from a status section.
- Add missing docs/SETUP_COSYVOICE.md placeholder with clear local-only notes.

### Phase B - Make Fresh Clone Work

- Add root package.json.
- Fix tts_cli.py project root detection.
- Add pipeline/preflight.mjs or pipeline/preflight.py.
- Make build_episode.sh fail early with actionable errors.

### Phase C - Productize One Demo Per Content Type

- demo-industry: HyperFrames pipeline reference.
- demo-data: HyperFrames chart reference.
- demo-manim: real Manim technical animation reference.

### Phase D - Add CI And Release Tags

- Add syntax/smoke CI once GitHub token has workflow permission.
- Tag the current state as prototype only after Phase A/B.
- Tag a real v0.2.0 after fresh clone can render a demo locally.

## Current Health Check

Checked locally on 2026-05-18:

- git status --short: clean before this audit file.
- make check: local dependencies present.
- python3 -m py_compile: passed for pipeline Python files.
- node --check pipeline/*.mjs: passed.

## Ownership Note

The project should be treated as a promising working prototype, not a finished standard open-source tool yet. The next work should prioritize reproducibility and boundary cleanup before adding more video features.
