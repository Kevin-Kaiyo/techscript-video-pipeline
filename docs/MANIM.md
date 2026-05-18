# Manim Renderer

Manim is now the reference renderer for technical-principle scenes.

## Current Demo

`episodes/demo-manim/` renders a Micro LED mass-transfer explainer:

- LED wafer pixel array
- elastomer transfer stamp
- alignment and release onto a TFT backplane
- defect/yield callouts

## Setup

```bash
python3.11 -m venv .venv-manim
.venv-manim/bin/pip install -r requirements-manim.txt
```

## Build

```bash
PYTHON=.venv-tts/bin/python make tts EP=demo-manim
make schedule EP=demo-manim
make manim-build EP=demo-manim
```

Output:

```text
episodes/demo-manim/output/demo-manim_full.mp4
```

## Notes

- Keep Manim in `.venv-manim`; do not install it into `.venv-tts`.
- Generated Manim media under `media/` is ignored by git.
- The Pythagoras files under `pipeline/manim/` are style references, not the primary product demo.
