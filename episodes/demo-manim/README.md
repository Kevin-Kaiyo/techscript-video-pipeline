# demo-manim - Micro LED Mass Transfer

This demo is the Phase C reference for technical-principle videos rendered with Manim.

It explains Micro LED mass transfer:

1. LED wafer pixels are fabricated densely.
2. An elastomer stamp picks up many pixels at once.
3. The stamp aligns and releases pixels onto a TFT backplane.
4. Yield, placement accuracy, defect detection, and repair determine whether the process can scale.

## Files

- `script.md` - narration split into `sNN` segments.
- `../../pipeline/manim/microled_mass_transfer.py` - Manim scene.
- `audio/voiceover/` - generated locally by `tts_cli.py` and ignored by git.
- `output/` - generated local MP4 files and ignored by git.

## Build

```bash
python3.11 -m venv .venv-manim
.venv-manim/bin/pip install -r requirements-manim.txt

PYTHON=.venv-tts/bin/python make tts EP=demo-manim
make schedule EP=demo-manim
make manim-build EP=demo-manim
```

The final video is written to:

```text
episodes/demo-manim/output/demo-manim_full.mp4
```
