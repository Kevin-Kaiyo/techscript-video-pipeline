# Makefile — TechScript Video Pipeline
#
# 用法:
#   make build EP=demo-industry      # Build one episode
#   make tts EP=demo-industry        # Generate Edge TTS voiceover
#   make schedule EP=demo-industry   # Generate audio schedule
#   make preflight EP=demo-industry  # Check build prerequisites
#   make ep01           # 完整构建 EP01
#   make ep01-render    # 只渲染动画（无配音）
#   make ep01-mix       # 只重新合成配音（视频已存在）
#   make preview EP=ep01 T=2,7,15,18,26,38,50,55    # 关键帧预览
#   make clean-frames EP=ep01

SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
EP ?= ep01
FPS ?= $(shell node -e "const fs=require('fs'); const p='shared/brand/video.json'; const c=fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')):{}; console.log(c.fps || 24)" 2>/dev/null || echo 24)
PYTHON ?= python3

.PHONY: help build manim-build tts schedule preflight ep01 ep01-render ep01-mix preview clean-frames check

help:
	@echo "Targets:"
	@echo "  make build EP=demo-industry             — Build an episode"
	@echo "  make manim-build EP=demo-manim          — Build Manim episode"
	@echo "  make tts EP=demo-industry               — Generate Edge TTS voiceover"
	@echo "  make schedule EP=demo-industry          — Generate audio_schedule.json"
	@echo "  make preflight EP=demo-industry         — Check build prerequisites"
	@echo "  make ep01                              — Build full ep01"
	@echo "  make ep01-render                       — Render animation only (silent)"
	@echo "  make ep01-mix                          — Re-mix audio onto existing silent video"
	@echo "  make preview EP=ep01 T=2,7,15,50       — Capture preview frames at given times"
	@echo "  make check                             — Check dependencies"
	@echo "  make clean-frames EP=ep01              — Remove /tmp frames cache"

build:
	@./pipeline/build_episode.sh $(EP)

manim-build:
	@./pipeline/build_manim_episode.sh $(EP)

tts:
	@$(PYTHON) pipeline/tts_cli.py --provider edge --voice zh-CN-YunjianNeural --ep $(EP)

schedule:
	@node pipeline/auto_schedule.mjs episodes/$(EP)

preflight:
	@node pipeline/preflight.mjs $(EP)

ep01: ; @./pipeline/build_episode.sh ep01
ep02: ; @./pipeline/build_episode.sh ep02
ep03: ; @./pipeline/build_episode.sh ep03

ep01-render:
	@BATCH=100 ./pipeline/build_episode.sh ep01 || true
	@ls -lh episodes/ep01/animations/hyperframes/renders/ep01_silent.mp4

ep01-mix:
	@node pipeline/compose_audio.mjs \
	  episodes/ep01/animations/hyperframes/renders/ep01_silent.mp4 \
	  episodes/ep01/audio/voiceover \
	  episodes/ep01/audio_schedule.json \
	  episodes/ep01/output/ep01_full.mp4 \
	  58

preview:
	@T="$${T:-2,15,30,45,55}"; \
	EP="$${EP:-ep01}"; \
	lsof -ti:18234 | xargs kill -9 2>/dev/null || true; \
	cd episodes/$$EP/animations/hyperframes && python3 -m http.server 18234 > /tmp/srv.log 2>&1 & disown; \
	sleep 2; \
	pkill -9 -f "Google\\ Chrome" 2>/dev/null || true; sleep 2; \
	rm -rf /tmp/chrome-render-profile; \
	node -e "require.resolve('ws')" >/dev/null || { echo 'Run npm install first'; exit 1; }; \
	COMP=$$(grep -o 'data-composition-id="[^"]*"' episodes/$$EP/animations/hyperframes/index.html | head -1 | sed 's/.*"\(.*\)"/\1/'); \
	mkdir -p preview/$$EP; \
	node pipeline/preview_shots.mjs \
	  http://localhost:18234/index.html $$COMP $$T \
	  $(PROJECT_ROOT)/preview/$$EP/p

clean-frames:
	@rm -rf /tmp/$(EP)_frames /tmp/full_frames
	@echo "✓ frame cache cleared"

check:
	@echo "── Dependency check ──"
	@which ffmpeg && ffmpeg -version | head -1 || echo "❌ ffmpeg missing"
	@which node && node --version || echo "❌ node missing"
	@which python3 && python3 --version || echo "❌ python3 missing"
	@[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && echo "✓ Chrome found" || echo "❌ Chrome missing"
	@which bc && echo "✓ bc found" || echo "❌ bc missing"
	@[ -d node_modules/ws ] && echo "✓ node dependency ws found" || echo "❌ run npm install"
	@[ -x .venv-manim/bin/python ] && .venv-manim/bin/python -m manim --version | head -1 || echo "❌ run python3.11 -m venv .venv-manim && .venv-manim/bin/pip install -r requirements-manim.txt"
