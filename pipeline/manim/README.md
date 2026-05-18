# Manim Renderer

Manim is the renderer for technical-principle scenes: geometry, algorithms, manufacturing processes, optics, and other step-by-step explanations.

## Environment

Use a dedicated Python 3.11 virtual environment:

```bash
python3.11 -m venv .venv-manim
.venv-manim/bin/pip install -r requirements-manim.txt
```

Do not install Manim into `.venv-tts`; TTS and Manim have different dependency profiles.

## Micro LED Mass Transfer Demo

```bash
PYTHON=.venv-tts/bin/python make tts EP=demo-manim
make schedule EP=demo-manim
make manim-build EP=demo-manim
```

Scene file:

```text
pipeline/manim/microled_mass_transfer.py
```

Output:

```text
episodes/demo-manim/output/demo-manim_full.mp4
```

## Legacy Pythagoras Examples

`pythagoras.py` and `pythagoras_nolatex.py` are kept as Manim style references. They are not the primary product demo.
