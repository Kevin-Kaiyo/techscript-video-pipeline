#!/usr/bin/env bash
set -euo pipefail

EP="${1:-demo-manim}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EP_DIR="$PROJECT_ROOT/episodes/$EP"
SCENE_FILE="${SCENE_FILE:-$PROJECT_ROOT/pipeline/manim/microled_mass_transfer.py}"
SCENE_CLASS="${SCENE_CLASS:-MicroLEDMassTransfer}"
MANIM_PYTHON="${MANIM_PYTHON:-$PROJECT_ROOT/.venv-manim/bin/python}"
QUALITY="${QUALITY:--qm}"
OUT_DIR="$EP_DIR/output"
SCHEDULE="$EP_DIR/audio_schedule.json"
VOICE_DIR="$EP_DIR/audio/voiceover"

mkdir -p "$OUT_DIR"

if [ ! -x "$MANIM_PYTHON" ]; then
  echo "ERROR: Manim Python not found: $MANIM_PYTHON"
  echo "Run: python3.11 -m venv .venv-manim && .venv-manim/bin/pip install -r requirements-manim.txt"
  exit 1
fi

"$MANIM_PYTHON" -m manim --version >/dev/null

cd "$PROJECT_ROOT"
"$MANIM_PYTHON" -m manim "$QUALITY" "$SCENE_FILE" "$SCENE_CLASS"

MANIM_VIDEO="$(find "$PROJECT_ROOT/media/videos" -name "${SCENE_CLASS}.mp4" -type f | sort | tail -1)"
if [ -z "$MANIM_VIDEO" ] || [ ! -f "$MANIM_VIDEO" ]; then
  echo "ERROR: rendered Manim video not found for $SCENE_CLASS"
  exit 1
fi

SILENT="$OUT_DIR/${EP}_silent.mp4"
cp "$MANIM_VIDEO" "$SILENT"
echo "Rendered silent video: $SILENT"

if [ -f "$SCHEDULE" ]; then
  DURATION="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SILENT")"
  node "$PROJECT_ROOT/pipeline/compose_audio.mjs" \
    "$SILENT" "$VOICE_DIR" "$SCHEDULE" "$OUT_DIR/${EP}_full.mp4" "$DURATION"
  echo "Final video: $OUT_DIR/${EP}_full.mp4"
else
  echo "WARN: no audio_schedule.json found; keeping silent output only."
fi
