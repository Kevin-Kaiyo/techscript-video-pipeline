#!/usr/bin/env python3
"""
Micro LED EP01 视频合成器（Python 版）
不依赖 libass，用 ffmpeg drawtext 烧制字幕
"""

import os
import subprocess
import json
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE, "assets", "images")
VO_DIR  = os.path.join(BASE, "assets", "audio", "voiceover")
BGM_DIR = os.path.join(BASE, "assets", "audio", "bgm")
OUTPUT  = os.path.join(BASE, "output", "ep01_microled_intro.mp4")
TMPDIR  = "/tmp/microled_ep01"
os.makedirs(os.path.join(BASE, "output"), exist_ok=True)
os.makedirs(TMPDIR, exist_ok=True)

FONT_CN = "/System/Library/Fonts/Hiragino Sans GB.ttc"

# 场景数据：(图像文件名, 配音文件名, 字幕文本)
SCENES = [
    ("ep01_s01_opening.jpg",    "ep01_s01.mp3", "你有没有想过|手机屏幕里的光，是怎么来的？"),
    ("ep01_s02_comparison.jpg", "ep01_s02.mp3", "传统LCD靠背光|OLED自发光但有烧屏风险"),
    ("ep01_s03_reveal.jpg",     "ep01_s03.mp3", "Micro LED|是下一个时代的答案"),
    ("ep01_s04_principle.jpg",  "ep01_s04.mp3", "几百万颗微型LED|每个像素都是独立的灯"),
    ("ep01_s05_advantages.jpg", "ep01_s05.mp3", "亮度10倍 · 寿命10万小时 · 零烧屏"),
    ("ep01_s06_applications.jpg","ep01_s06.mp3","小小的像素，大大的未来"),
]

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        print(result.stderr[-1000:])
        raise RuntimeError(result.stderr)
    return result

def get_duration(path):
    r = run(f'ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{path}"')
    return float(r.stdout.strip())

def escape_drawtext(s):
    """转义 ffmpeg drawtext 文本"""
    return s.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")

print("🎬 Micro LED EP01 视频合成开始...")
print("━" * 50)

# Step 1: 为每个场景生成视频（图+音+字幕）
scene_files = []
for i, (img_name, vo_name, subtitle) in enumerate(SCENES):
    img_path = os.path.join(IMG_DIR, img_name)
    vo_path  = os.path.join(VO_DIR, vo_name)
    out_path = os.path.join(TMPDIR, f"scene_{i+1:02d}.mp4")

    dur = get_duration(vo_path)
    print(f"  → Scene {i+1}/6: {dur:.2f}s  {subtitle[:20]}...")

    # 处理双行字幕
    lines = subtitle.split("|")
    if len(lines) == 2:
        line1, line2 = lines[0], lines[1]
        # 两行字幕，竖向排列
        sub_filter = (
            f"drawtext=fontfile='{FONT_CN}':text='{escape_drawtext(line1)}':"
            f"fontsize=42:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-120:enable='between(t,0,{dur})',"
            f"drawtext=fontfile='{FONT_CN}':text='{escape_drawtext(line2)}':"
            f"fontsize=42:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-65:enable='between(t,0,{dur})'"
        )
    else:
        line1 = lines[0]
        sub_filter = (
            f"drawtext=fontfile='{FONT_CN}':text='{escape_drawtext(line1)}':"
            f"fontsize=42:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-90:enable='between(t,0,{dur})'"
        )

    # Bake subtitle into image using Pillow (ffmpeg lacks drawtext/freetype)
    from PIL import Image as PILImage, ImageDraw as PILDraw, ImageFont as PILFont

    base_img = PILImage.open(img_path).convert("RGB").resize((1920, 1080))
    draw_img = PILDraw.Draw(base_img)

    def draw_sub_line(text, y_offset):
        try:
            fnt = PILFont.truetype(FONT_CN, 44, index=0)
        except Exception:
            fnt = PILFont.load_default()
        bbox = draw_img.textbbox((0, 0), text, font=fnt)
        tw = bbox[2] - bbox[0]
        x = (1920 - tw) // 2
        # shadow
        draw_img.text((x+2, y_offset+2), text, font=fnt, fill=(0, 0, 0, 200))
        draw_img.text((x,   y_offset),   text, font=fnt, fill=(255, 255, 255))

    lines = subtitle.split("|")
    if len(lines) == 2:
        draw_sub_line(lines[0], 1080 - 125)
        draw_sub_line(lines[1], 1080 - 72)
    else:
        draw_sub_line(lines[0], 1080 - 95)

    sub_img_path = os.path.join(TMPDIR, f"scene_{i+1:02d}_sub.jpg")
    base_img.save(sub_img_path, "JPEG", quality=95)

    cmd = (
        f'ffmpeg -loop 1 -i "{sub_img_path}" -i "{vo_path}" '
        f'-vf "scale=1920:1080,setsar=1" '
        f'-c:v libx264 -tune stillimage -preset fast -crf 22 '
        f'-c:a aac -b:a 128k '
        f'-pix_fmt yuv420p '
        f'-t {dur} -shortest '
        f'"{out_path}" -y -loglevel error'
    )
    run(cmd)
    scene_files.append(out_path)
    print(f"    ✅ scene_{i+1:02d}.mp4")

# Step 2: 拼接所有场景
print("\n🔗 Step 2: 拼接场景...")
concat_list = os.path.join(TMPDIR, "concat.txt")
with open(concat_list, "w") as f:
    for sf in scene_files:
        f.write(f"file '{sf}'\n")

concat_out = os.path.join(TMPDIR, "concat.mp4")
run(f'ffmpeg -f concat -safe 0 -i "{concat_list}" -c copy "{concat_out}" -y -loglevel error')
print("✅ 拼接完成")

# Step 3: 叠加背景音乐（如果存在）
bgm_files = [f for f in os.listdir(BGM_DIR) if f.endswith(".mp3")] if os.path.exists(BGM_DIR) else []
bgm_candidates = [os.path.join(BGM_DIR, f) for f in bgm_files if "ep01" in f.lower() or "bgm" in f.lower()]

total_dur = sum(get_duration(os.path.join(VO_DIR, s[1])) for s in SCENES)

if bgm_candidates:
    bgm_path = bgm_candidates[0]
    print(f"\n🎵 Step 3: 叠加背景音乐 ({os.path.basename(bgm_path)})...")
    bgm_out = os.path.join(TMPDIR, "with_bgm.mp4")
    fade_out_start = max(0, total_dur - 3)
    cmd = (
        f'ffmpeg -i "{concat_out}" -i "{bgm_path}" '
        f'-filter_complex "[1:a]volume=0.12,afade=t=in:st=0:d=2,afade=t=out:st={fade_out_start:.1f}:d=3[bgm];'
        f'[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]" '
        f'-map 0:v -map "[aout]" '
        f'-c:v copy -c:a aac -b:a 192k '
        f'"{bgm_out}" -y -loglevel error'
    )
    run(cmd)
    final_input = bgm_out
    print("✅ 背景音乐叠加完成")
else:
    print("\n🎵 Step 3: 背景音乐未就绪，跳过（可后续重新合成）")
    final_input = concat_out

# Step 4: 最终输出（重新编码确保兼容性）
print("\n📦 Step 4: 最终输出...")
run(
    f'ffmpeg -i "{final_input}" '
    f'-c:v libx264 -preset medium -crf 18 '
    f'-c:a aac -b:a 192k '
    f'-movflags +faststart '
    f'"{OUTPUT}" -y -loglevel error'
)

# 输出信息
dur = get_duration(OUTPUT)
size = os.path.getsize(OUTPUT)
print(f"\n{'━'*50}")
print(f"🎉 视频合成完成！")
print(f"📁 输出：{OUTPUT}")
print(f"⏱  时长：{dur:.2f} 秒")
print(f"📦 文件大小：{size // 1024 // 1024:.1f} MB")
print(f"🖥  规格：1920×1080 | H.264 | 30fps")

# 清理临时文件
shutil.rmtree(TMPDIR, ignore_errors=True)
print("🧹 临时文件已清理")
