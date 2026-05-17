#!/usr/bin/env python3
"""Wide bake-off: ALL voices of all available providers."""
from __future__ import annotations
import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.tts import list_providers, get_provider

TEXT = "微LED是新一代显示技术。它由数百万颗极小的发光二极管组成，每颗只有头发丝直径的十分之一。这意味着更亮、更省电、寿命更长，是未来五年最值得关注的赛道。"
OUT = Path.home() / "Projects/techscript-video-pipeline/tts-bake-off"
OUT.mkdir(parents=True, exist_ok=True)

# Provider 黑名单（写音色太多/费钱）
LIMIT = {"google": 4, "edge": 6, "elevenlabs": 2, "cosyvoice": 1, "minimax": 0}

results = []
for name in list_providers():
    if LIMIT.get(name, 0) == 0:
        continue
    p = get_provider(name)
    ok, reason = p.available()
    if not ok:
        print(f"⛔ skip {name}: {reason}"); continue
    for vid in list(p.voices.keys())[:LIMIT.get(name, 99)]:
        safe = vid.replace("/", "_").replace("zh-CN-", "")
        out = OUT / f"{name}__{safe}.mp3"
        print(f"🔊 {name} / {vid} …", end="", flush=True)
        try:
            p.synth(TEXT, out, voice=vid)
            d = float(subprocess.check_output(
                ["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0", str(out)]
            ).decode().strip())
            sz = out.stat().st_size // 1024
            print(f"  ✓ {d:.1f}s  {sz}KB  → {out.name}")
            results.append((name, vid, out, d))
        except Exception as e:
            print(f"  ❌ {type(e).__name__}: {e}")

print(f"\n🎉 {len(results)} versions in {OUT}")
