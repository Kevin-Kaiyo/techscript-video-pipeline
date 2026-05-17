#!/usr/bin/env python3
"""
Micro LED EP01 字幕文件生成器
根据各段配音时长生成 SRT 字幕
"""

import subprocess
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO_DIR = os.path.join(BASE, "assets", "audio", "voiceover")
OUTPUT = os.path.join(BASE, "assets", "ep01_subtitles.srt")

def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def fmt_time(secs):
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int((secs % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

subtitles = [
    "你有没有想过\n手机屏幕里的光，是怎么来的？",
    "传统屏幕靠背光灯照亮液晶\nOLED 每个像素自己发光，但有烧屏风险",
    "而 Micro LED\n是下一个时代的答案",
    "几百万颗微型 LED\n每一个像素都是一盏独立的灯",
    "亮度是 OLED 的十倍 ☀️\n寿命十万小时 | 零烧屏风险",
    "智能手表 · AR眼镜 · 汽车大灯 · 拼接大屏\n小小的像素，大大的未来",
]

files = [os.path.join(VO_DIR, f"ep01_s0{i+1}.mp3") for i in range(6)]

srt_content = ""
t = 0.0
for i, (f, sub) in enumerate(zip(files, subtitles)):
    dur = get_duration(f)
    start = t
    end = t + dur
    srt_content += f"{i+1}\n{fmt_time(start)} --> {fmt_time(end)}\n{sub}\n\n"
    t = end

with open(OUTPUT, "w", encoding="utf-8") as fh:
    fh.write(srt_content)

print(f"✅ 字幕文件：{OUTPUT}")
print(f"📊 总时长：{t:.2f} 秒")
print("\n字幕内容预览：")
print(srt_content[:500])
