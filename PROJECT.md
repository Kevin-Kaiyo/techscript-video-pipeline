# PROJECT.md - TechScript Video Pipeline

## Project Status

TechScript Video Pipeline is a local-first workflow for turning technical scripts into short explainer videos with animation, voiceover, subtitles, and FFmpeg composition.

The first validated demos use Micro LED because it is the seed domain, but the product goal is broader: a reusable semiconductor explainer pipeline for topics such as advanced packaging, hybrid bonding, photonic interconnects, semiconductor equipment/materials, display technology, and market/industry analysis.

Current status: **prototype / stabilization phase**.

The project has working HyperFrames and Manim paths plus a usable TTS abstraction layer, but it is not yet a polished end-user product. The immediate goal is reproducibility and repeatability: a fresh clone should be understandable, installable, and able to render representative demos from both rendering lines locally.

## Product Scope

### In Scope

- Episode-based project layout under `episodes/<episode>/`.
- HyperFrames rendering for industry maps, equipment/material flows, comparison, roadmap, and data-chart videos.
- Manim rendering for technical principles, process mechanics, geometry, algorithms, and manufacturing sequence videos.
- TTS generation through pluggable providers.
- Automatic audio scheduling from generated voiceover duration.
- FFmpeg video/audio composition.
- Semiconductor-topic authoring patterns that can be reused beyond Micro LED.

### Out of Scope For The Current Phase

- Cloud rendering.
- One-click publishing to Bilibili, YouTube, TikTok, or LinkedIn.
- Automatic LLM script generation.
- Commercial GSAP use without a separate GSAP commercial license.
- Bundling generated media, voice samples, or personal assets in git.
- Remotion integration until HyperFrames becomes a proven maintenance bottleneck.

## Canonical Workflow

```text
episodes/<ep>/script.md
  -> pipeline/tts_cli.py
  -> episodes/<ep>/audio/voiceover/*.mp3
  -> pipeline/auto_schedule.mjs
  -> episodes/<ep>/audio_schedule.json
  -> choose renderer:
       HyperFrames: episodes/<ep>/animations/hyperframes/index.html
       Manim:       pipeline/manim/<scene>.py
  -> build_episode.sh or build_manim_episode.sh
  -> episodes/<ep>/output/<ep>_full.mp4
```

## Content Types

| Content type | Primary renderer | Status |
| --- | --- | --- |
| Industry maps / value chains | HyperFrames | Working demos |
| Equipment/material/process maps | HyperFrames | Pattern documented |
| Data, market, and roadmap explainers | HyperFrames | Working demos |
| Technical principles / process mechanics | Manim | Reference demo available |
| Mixed episodes | HyperFrames + Manim + FFmpeg | Planned composition pattern |

## Topic Families

The pipeline should support repeatable semiconductor explainers across these families:

| Family | Example questions | Preferred renderer |
| --- | --- | --- |
| Technology principle | How does hybrid bonding actually connect two wafers? | Manim |
| Manufacturing process | What happens from surface preparation to post-bond anneal? | Manim |
| Equipment/material stack | Which tools and materials are needed for hybrid bonding? | HyperFrames |
| Industry/value chain | Who supplies tools, materials, substrates, foundry capacity, and inspection? | HyperFrames |
| Market/data story | Why is 3D packaging becoming necessary now? | HyperFrames |
| System architecture | How do CPO, optical engines, switch ASICs, and packaging interact? | HyperFrames, with Manim inserts when needed |

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

### Phase D - Generalize Beyond Micro LED

- Reframe docs and templates around semiconductor explainer topics rather than one Micro LED series. Done.
- Keep HyperFrames and Manim as the two supported production renderers. Done.
- Add topic families and renderer selection rules. Done.
- Add a scaffold command for new episodes by content type. Done.
- Produce one non-Micro LED reference episode, preferably hybrid bonding or 3D packaging. Planned.

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
