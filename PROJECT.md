# PROJECT.md - TechScript Video Pipeline

## Project Status

TechScript Video Pipeline is a local-first workflow for turning technical scripts into short explainer videos with animation, voiceover, subtitles, and FFmpeg composition.

Current status: **prototype / stabilization phase**.

The project has a working HyperFrames path and a usable TTS abstraction layer, but it is not yet a polished end-user product. The immediate goal is reproducibility: a fresh clone should be understandable, installable, and able to render at least one demo locally.

## Product Scope

### In Scope

- Episode-based project layout under `episodes/<episode>/`.
- HyperFrames rendering for industry, process, comparison, and data-chart videos.
- TTS generation through pluggable providers.
- Automatic audio scheduling from generated voiceover duration.
- FFmpeg video/audio composition.
- Manim integration for technical/math scenes, once a real demo is productized.

### Out of Scope For The Current Phase

- Cloud rendering.
- One-click publishing to Bilibili, YouTube, TikTok, or LinkedIn.
- Automatic LLM script generation.
- Commercial GSAP use without a separate GSAP commercial license.
- Bundling generated media, voice samples, or personal assets in git.

## Canonical Workflow

```text
episodes/<ep>/script.md
  -> pipeline/tts_cli.py
  -> episodes/<ep>/audio/voiceover/*.mp3
  -> pipeline/auto_schedule.mjs
  -> episodes/<ep>/audio_schedule.json
  -> episodes/<ep>/animations/hyperframes/index.html
  -> pipeline/build_episode.sh
  -> episodes/<ep>/output/<ep>_full.mp4
```

## Content Types

| Content type | Primary renderer | Status |
| --- | --- | --- |
| Industry maps / value chains | HyperFrames | Working demos |
| Data and chart explainers | HyperFrames | Working demos |
| Technical principles / algorithms | Manim | Reference demo available |

## Current Demos

| Episode | Purpose | Renderer | Status |
| --- | --- | --- | --- |
| `demo-industry` | Micro LED industry chain | HyperFrames | Reference demo |
| `demo-data` | Display market growth | HyperFrames | Reference demo |
| `demo-tech` | Micro LED mass transfer concept | HyperFrames | Temporary technical demo |
| `demo-manim` | Micro LED mass transfer | Manim | Reference demo |
| `ep01` | Original Micro LED experiment | Mixed legacy/current | Kept as historical material |

## Stabilization Plan

### Phase A - Make The Repository Honest

- Keep current public docs aligned with actual commands and directory structure.
- Archive legacy EP01 static-image scripts instead of presenting them as the main pipeline.
- Mark Manim as planned until a real demo exists.
- Document current risks and open problems.

### Phase B - Make Fresh Clone Work

- Use a root `package.json` for Node dependencies instead of `/tmp/node_modules`.
- Add preflight checks before rendering.
- Fix project-root path assumptions.
- Use `shared/brand/video.json` as the default video configuration source.

### Phase C - Productize Manim

- Build a real `demo-manim` episode. Done.
- Document the Manim setup and rendering path. Done.
- Use it for technical/algorithmic scenes rather than treating it as a future promise. Done for the first reference demo.

## Verification Baseline

Before considering a change stable, run:

```bash
npm install
npm run check
make check
```

For a real render smoke test:

```bash
source .venv-tts/bin/activate
python pipeline/tts_cli.py --provider edge --voice zh-CN-YunjianNeural --ep demo-industry
node pipeline/auto_schedule.mjs episodes/demo-industry
bash pipeline/build_episode.sh demo-industry
```
