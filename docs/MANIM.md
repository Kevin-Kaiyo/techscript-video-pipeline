# Manim Renderer

Manim is now the reference renderer for technical-principle scenes.

Use Manim when the audience needs to understand motion, geometry, contact, alignment, physical mechanism, or process sequence. In semiconductor explainers, this usually means the “how it works” part rather than the “who supplies what” part.

## Current Demo

`episodes/demo-manim/` renders a Micro LED mass-transfer explainer:

- LED wafer pixel array
- elastomer transfer stamp
- alignment and release onto a TFT backplane
- defect/yield callouts

## Good Future Topics

- Hybrid bonding: surface planarization, oxide/copper contact, alignment, anneal, void defects.
- 3D packaging: chiplet placement, TSV/interposer routing, stacked thermal paths.
- Micro LED optical interconnects: emitter array, coupling path, micro-optics, receiver alignment.
- Lithography or etch basics: mask, exposure, pattern transfer, process window.

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
- Use HyperFrames, not Manim, for company maps, equipment/material matrices, market charts, and timeline slides.
