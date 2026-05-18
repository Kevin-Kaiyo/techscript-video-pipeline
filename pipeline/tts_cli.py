#!/usr/bin/env python3
"""Unified TTS CLI — provider/voice pluggable.

Usage:
  python tts_cli.py --list                              # 列出 provider/voice
  python tts_cli.py --provider edge --voice zh-CN-YunxiNeural --text "你好" --out out.mp3
  python tts_cli.py --ep demo-tech --provider edge --voice zh-CN-YunxiNeural   # 按 script.md 整集生成
  python tts_cli.py --bake-off "Micro LED 是新一代显示技术"   # 同段话跑所有可用 provider 并输出对比文件
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import tts as tts_pkg
from pipeline.tts import list_providers, get_provider

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SEG_RE = re.compile(r'^##\s+(s\d+)\s*\n([\s\S]*?)(?=^##\s+s\d+|\Z)', re.M)


def parse_script(path: Path):
    txt = path.read_text(encoding="utf-8")
    segs = []
    for m in SCRIPT_SEG_RE.finditer(txt):
        sid = m.group(1)
        body = m.group(2).strip()
        # 去掉 ✦…、() 标注、空行
        body = re.sub(r'\([^)]*\)', '', body)
        body = re.sub(r'\(（[^）]*）\)', '', body)
        body = re.sub(r'^\s*[✦•·\-]\s*', '', body, flags=re.M)
        body = "\n".join(line.strip() for line in body.splitlines() if line.strip())
        if body:
            segs.append((sid, body))
    return segs


def cmd_list():
    print("\n📚 可用 TTS Providers:\n")
    for name in list_providers():
        p = get_provider(name)
        ok, reason = p.available()
        flag = "✅" if ok else "⛔"
        print(f"  {flag} {name:12s}  — {reason}")
        for vid, desc in p.voices.items():
            print(f"        🔊 {vid:32s}  {desc}")
        print()


def cmd_synth_text(provider, voice, text, out):
    p = get_provider(provider)
    out_path = Path(out)
    p.synth(text, out_path, voice=voice)
    print(f"✓ {out_path}")


def cmd_synth_ep(provider, voice, ep):
    ep_dir = PROJECT_ROOT / "episodes" / ep
    script = ep_dir / "script.md"
    if not script.exists():
        print(f"❌ {script} 不存在"); sys.exit(1)
    out_dir = ep_dir / "audio/voiceover"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = get_provider(provider)
    segs = parse_script(script)
    valid_outputs = {f"{ep}_{sid}.mp3" for sid, _ in segs}
    for stale in out_dir.glob(f"{ep}_s*.mp3"):
        if stale.name not in valid_outputs:
            stale.unlink()
            print(f"  removed stale {stale.name}")
    print(f"📖 {ep}: {len(segs)} 段, provider={provider}, voice={voice or p.default_voice}")
    for sid, text in segs:
        out = out_dir / f"{ep}_{sid}.mp3"
        print(f"  → {sid}: {text[:60]}{'...' if len(text)>60 else ''}")
        p.synth(text, out, voice=voice)
        # duration
        import subprocess
        d = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0", str(out)]).decode().strip()
        print(f"     ✓ {out.name}  {float(d):.2f}s")


def cmd_bake_off(text, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    print(f"🎤 Bake-off: \"{text}\"\n")
    results = []
    for name in list_providers():
        p = get_provider(name)
        ok, reason = p.available()
        if not ok:
            print(f"  ⛔ skip {name}: {reason}")
            continue
        # 每 provider 跑前 2 个音色
        voice_ids = list(p.voices.keys())[:2]
        for vid in voice_ids:
            safe = vid.replace("/", "_")
            out = out_dir / f"{name}__{safe}.mp3"
            print(f"  🔊 {name} / {vid} …", end="", flush=True)
            try:
                p.synth(text, out, voice=vid)
                import subprocess
                d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0", str(out)]).decode().strip())
                print(f" ✓ {d:.1f}s  → {out.name}")
                results.append((name, vid, out, d))
            except Exception as e:
                print(f" ❌ {e}")
    print(f"\n🎉 共 {len(results)} 个版本，目录: {out_dir}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--provider", default="edge")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--text", default=None)
    ap.add_argument("--out", default="out.mp3")
    ap.add_argument("--ep", default=None)
    ap.add_argument("--bake-off", default=None, dest="bake_off")
    ap.add_argument("--bake-dir", default=str(PROJECT_ROOT / "tts-bake-off"))
    args = ap.parse_args()

    if args.list:
        cmd_list(); return
    if args.bake_off:
        cmd_bake_off(args.bake_off, args.bake_dir); return
    if args.ep:
        cmd_synth_ep(args.provider, args.voice, args.ep); return
    if args.text:
        cmd_synth_text(args.provider, args.voice, args.text, args.out); return
    ap.print_help()


if __name__ == "__main__":
    main()
