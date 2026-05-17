#!/usr/bin/env bash
# 自动重试 resumable 渲染脚本，直到完成
set -e
FPS=${1:-24}
DURATION=${2:-58}
FRAMES_DIR=${3:-/tmp/full_frames}
COMP_ID=${4:-microled-demo}
URL=${5:-http://localhost:18234/index.html}
BATCH=${6:-100}

TOTAL=$(echo "$FPS * $DURATION" | bc)
MAX_RUNS=30

for i in $(seq 1 $MAX_RUNS); do
  echo ""
  echo "═══════════ Run $i ═══════════"
  pkill -f "chrome-render-profile" 2>/dev/null || true
  rm -rf /tmp/chrome-render-profile 2>/dev/null || true
  sleep 1
  
  set +e
  cd /tmp && NODE_PATH=/tmp/node_modules node --expose-gc --max-old-space-size=400 \
    /tmp/render_cdp_resumable.mjs \
    "$FPS" "$DURATION" "$FRAMES_DIR" "$COMP_ID" "$URL" "$BATCH"
  EXIT_CODE=$?
  set -e
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 Rendering complete!"
    exit 0
  elif [ $EXIT_CODE -eq 2 ]; then
    continue
  else
    # SIGKILL etc., 等内存恢复后重试
    DONE=$(ls "$FRAMES_DIR" 2>/dev/null | wc -l | tr -d ' ')
    echo "⚠️  Exit $EXIT_CODE, done=$DONE/$TOTAL — sleep 3s and retry"
    sleep 3
  fi
done
echo "❌ Max runs ($MAX_RUNS) exceeded"
exit 1
