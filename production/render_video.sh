#!/bin/bash
# ============================================================
# Micro LED EP01 视频合成脚本
# 输入：场景图 + 配音 + 背景音乐 + 字幕
# 输出：output/ep01_microled_intro.mp4
# ============================================================

set -e
BASE="$(cd "$(dirname "$0")/.." && pwd)"
IMG_DIR="$BASE/assets/images"
VO_DIR="$BASE/assets/audio/voiceover"
BGM_DIR="$BASE/assets/audio/bgm"
OUTPUT="$BASE/output/ep01_microled_intro.mp4"
mkdir -p "$BASE/output"

echo "🎬 Micro LED EP01 视频合成开始..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 各场景持续时间（秒，与配音完全对齐）
DUR_S01=3.552
DUR_S02=10.841
DUR_S03=3.004
DUR_S04=11.729
DUR_S05=13.166
DUR_S06=15.151

# Step 1: 每个场景生成静态视频片段（图 + 配音）
echo "📽 Step 1: 生成各场景视频片段..."

scenes=(s01 s02 s03 s04 s05 s06)
durations=($DUR_S01 $DUR_S02 $DUR_S03 $DUR_S04 $DUR_S05 $DUR_S06)
imgs=(
  "ep01_s01_opening.jpg"
  "ep01_s02_comparison.jpg"
  "ep01_s03_reveal.jpg"
  "ep01_s04_principle.jpg"
  "ep01_s05_advantages.jpg"
  "ep01_s06_applications.jpg"
)

for i in "${!scenes[@]}"; do
  scene="${scenes[$i]}"
  dur="${durations[$i]}"
  img="$IMG_DIR/${imgs[$i]}"
  vo="$VO_DIR/ep01_${scene}.mp3"
  out="/tmp/ep01_${scene}.mp4"

  echo "  → Scene $((i+1))/6: ${scene} (${dur}s)"
  ffmpeg -loop 1 -i "$img" -i "$vo" \
    -c:v libx264 -tune stillimage -preset fast \
    -c:a aac -b:a 128k \
    -pix_fmt yuv420p \
    -t "$dur" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" \
    -shortest \
    "$out" -y -loglevel error
  echo "    ✅ $out"
done

# Step 2: 拼接所有场景
echo ""
echo "🔗 Step 2: 拼接场景..."

cat > /tmp/concat_list.txt << EOF
file '/tmp/ep01_s01.mp4'
file '/tmp/ep01_s02.mp4'
file '/tmp/ep01_s03.mp4'
file '/tmp/ep01_s04.mp4'
file '/tmp/ep01_s05.mp4'
file '/tmp/ep01_s06.mp4'
EOF

ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt \
  -c copy /tmp/ep01_concat.mp4 -y -loglevel error
echo "✅ 拼接完成"

# Step 3: 叠加背景音乐
echo ""
echo "🎵 Step 3: 叠加背景音乐..."

BGM_FILE="$BGM_DIR/ep01_bgm.mp3"

if [ -f "$BGM_FILE" ]; then
  ffmpeg -i /tmp/ep01_concat.mp4 -i "$BGM_FILE" \
    -filter_complex "[1:a]volume=0.12,afade=t=in:st=0:d=2,afade=t=out:st=54:d=3[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
    -map 0:v -map "[aout]" \
    -c:v copy -c:a aac -b:a 192k \
    /tmp/ep01_with_bgm.mp4 -y -loglevel error
  echo "✅ 背景音乐叠加完成"
  INPUT_FINAL="/tmp/ep01_with_bgm.mp4"
else
  echo "⚠️  未找到背景音乐，跳过此步骤"
  INPUT_FINAL="/tmp/ep01_concat.mp4"
fi

# Step 4: 烧制字幕
echo ""
echo "💬 Step 4: 烧制中文字幕..."

FONT_PATH="/System/Library/Fonts/Hiragino Sans GB.ttc"
SRT_FILE="$BASE/assets/ep01_subtitles.srt"

ffmpeg -i "$INPUT_FINAL" \
  -vf "subtitles='$SRT_FILE':force_style='FontName=Hiragino Sans GB,FontSize=38,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=3,Shadow=1,Alignment=2,MarginV=60'" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a copy \
  "$OUTPUT" -y -loglevel error

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 视频合成完成！"
echo "📁 输出：$OUTPUT"
echo ""

# 显示文件信息
ffprobe -v quiet -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUTPUT" 2>/dev/null | while IFS='=' read key val; do
  case $key in
    duration) printf "⏱ 时长：%.2f 秒\n" "$val" ;;
    size) printf "📦 文件大小：%d KB\n" $((val / 1024)) ;;
  esac
done
