#!/usr/bin/env bash
# build_episode.sh — 端到端构建一集视频
#
# 用法: ./pipeline/build_episode.sh ep01
#       ./pipeline/build_episode.sh ep02
#
# 前置条件:
# 1. episodes/<ep>/animations/hyperframes/index.html 存在
#    - <div id="stage" data-composition-id="<ep>-demo" data-duration="<SECS>">
#    - window.__timelines[<ep>-demo] = gsap.timeline(...)
# 2. episodes/<ep>/audio/voiceover/<ep>_s01.mp3 ... 等配音文件
# 3. episodes/<ep>/audio_schedule.json: [{"file":"s01.mp3", "start_ms": 300}, ...]

set -e
EP="${1:?Usage: $0 <ep01|ep02|...>}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EP_DIR="$PROJECT_ROOT/episodes/$EP"
HF_DIR="$EP_DIR/animations/hyperframes"
AV_DIR="$EP_DIR/audio/voiceover"
OUT_DIR="$EP_DIR/output"
RENDERS="$HF_DIR/renders"
FRAMES_DIR="/tmp/${EP}_frames"
PORT=18234

[ -d "$HF_DIR" ] || { echo "❌ $HF_DIR not found"; exit 1; }
mkdir -p "$RENDERS" "$OUT_DIR"

cd "$PROJECT_ROOT"
node pipeline/preflight.mjs "$EP"

# 1) 解析 composition id + duration
COMP_ID=$(grep -o 'data-composition-id="[^"]*"' "$HF_DIR/index.html" | head -1 | sed 's/.*"\(.*\)"/\1/')
DURATION=$(grep -o 'data-duration="[^"]*"' "$HF_DIR/index.html" | head -1 | sed 's/.*"\(.*\)"/\1/')
FPS=${FPS:-$(node -e "const fs=require('fs'); const p='shared/brand/video.json'; const c=fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')):{}; console.log(c.fps || 24)")}
TOTAL_FRAMES=$(echo "$FPS * $DURATION" | bc | cut -d. -f1)

echo "═══════════════════════════════════════"
echo " Episode:     $EP"
echo " Composition: $COMP_ID"
echo " Duration:    ${DURATION}s @ ${FPS}fps = $TOTAL_FRAMES frames"
echo " Output:      $OUT_DIR/${EP}_full.mp4"
echo "═══════════════════════════════════════"

# 2) 启动 HTTP server
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
cd "$HF_DIR" && nohup python3 -m http.server $PORT > /tmp/${EP}_server.log 2>&1 &
disown
sleep 2

# 3) 分批渲染，直到完成
MAX_RUNS=30
BATCH=${BATCH:-100}
for i in $(seq 1 $MAX_RUNS); do
  echo ""
  echo "── Render pass $i (batch=$BATCH) ──"
  pkill -9 -f "Google\\ Chrome.*chrome-render-profile" 2>/dev/null || true
  sleep 1
  rm -rf /tmp/chrome-render-profile

  set +e
  cd "$PROJECT_ROOT" && node --expose-gc --max-old-space-size=400 \
    pipeline/render_cdp_resumable.mjs \
    "$FPS" "$DURATION" "$FRAMES_DIR" "$COMP_ID" \
    "http://localhost:$PORT/index.html" "$BATCH"
  CODE=$?
  set -e

  case $CODE in
    0) echo "✅ All frames rendered"; break ;;
    2) continue ;;
    *) echo "⚠️ Exit $CODE — retry"; sleep 3 ;;
  esac
done

# 5) FFmpeg: silent mp4
echo ""
echo "── Encoding silent MP4 ──"
SILENT="$RENDERS/${EP}_silent.mp4"
ffmpeg -y -framerate $FPS -i "$FRAMES_DIR/frame_%05d.jpg" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart \
  "$SILENT" 2>&1 | tail -1

# 6) 合成配音
SCHEDULE="$EP_DIR/audio_schedule.json"
OUT="$OUT_DIR/${EP}_full.mp4"

if [ -f "$SCHEDULE" ]; then
  echo ""
  echo "── Mixing voiceover from $SCHEDULE ──"
  node "$PROJECT_ROOT/pipeline/compose_audio.mjs" \
    "$SILENT" "$AV_DIR" "$SCHEDULE" "$OUT" "$DURATION"
else
  echo "⚠️ No $SCHEDULE — silent output only"
  cp "$SILENT" "$OUT"
fi

echo ""
echo "═══════════════════════════════════════"
echo "🎉 $OUT"
ls -lh "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
