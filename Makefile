# Makefile — microled-science-video 一键构建
#
# 用法:
#   make ep01           # 完整构建 EP01
#   make ep01-render    # 只渲染动画（无配音）
#   make ep01-mix       # 只重新合成配音（视频已存在）
#   make preview EP=ep01 T=2,7,15,18,26,38,50,55    # 关键帧预览
#   make clean-frames EP=ep01

SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
EP ?= ep01
FPS ?= 24

.PHONY: help ep01 ep01-render ep01-mix preview clean-frames check

help:
	@echo "Targets:"
	@echo "  make ep01                              — Build full ep01"
	@echo "  make ep01-render                       — Render animation only (silent)"
	@echo "  make ep01-mix                          — Re-mix audio onto existing silent video"
	@echo "  make preview EP=ep01 T=2,7,15,50       — Capture preview frames at given times"
	@echo "  make check                             — Check dependencies"
	@echo "  make clean-frames EP=ep01              — Remove /tmp frames cache"

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
	[ -d /tmp/node_modules/ws ] || (cd /tmp && npm install ws --no-audit --no-fund > /dev/null 2>&1); \
	cp pipeline/preview_shots.mjs /tmp/ 2>/dev/null || true; \
	COMP=$$(grep -o 'data-composition-id="[^"]*"' episodes/$$EP/animations/hyperframes/index.html | head -1 | sed 's/.*"\(.*\)"/\1/'); \
	mkdir -p preview/$$EP; \
	cd /tmp && NODE_PATH=/tmp/node_modules node /tmp/preview_shots.mjs \
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
