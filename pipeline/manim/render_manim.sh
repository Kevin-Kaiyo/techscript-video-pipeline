#!/usr/bin/env bash
set -euo pipefail

SCENE_FILE="${1:-scenes/pythagoras.py}"
SCENE_CLASS="${2:-PythagoreanTheorem}"
QUALITY="${QUALITY:--qh}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIM_ROOT="${MANIM_ROOT:-$HOME/Projects/manim-math}"

cd "$MANIM_ROOT"
source .venv/bin/activate
export PATH="/Library/TeX/texbin:$PATH"

# Copy scene into manim project working dir for stable relative imports/media paths
cp "$ROOT/$SCENE_FILE" ./_pipeline_scene.py
manim "$QUALITY" _pipeline_scene.py "$SCENE_CLASS" >&2

OUT="media/videos/_pipeline_scene/1080p60/${SCENE_CLASS}.mp4"
mkdir -p "$ROOT/outputs"
cp "$OUT" "$ROOT/outputs/${SCENE_CLASS}_silent.mp4"
echo "$ROOT/outputs/${SCENE_CLASS}_silent.mp4"
