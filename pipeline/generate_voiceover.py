#!/usr/bin/env python3
"""
generate_voiceover.py — 用 CosyVoice 给一集生成所有配音段

用法:
  cd ~/Projects/cosyvoice_local
  source .venv/bin/activate
  python /Users/kimmy/Projects/techscript-video-pipeline/pipeline/generate_voiceover.py \
    --ep ep02 \
    --voice "中文男"

输入: episodes/<ep>/script.md (markdown, 每段 ## sNN 开头)
输出: episodes/<ep>/audio/voiceover/<ep>_sNN.mp3

script.md 格式:
## s01
你有没有想过，手机屏幕里的「光」是怎么来的？

## s02
LCD 靠背光...
"""
import argparse, re, os, sys, subprocess
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'Projects/cosyvoice_local'))
sys.path.insert(0, str(Path.home() / 'Projects/cosyvoice_local/third_party/Matcha-TTS'))
import torchaudio
from cosyvoice.cli.cosyvoice import AutoModel

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', default=str(Path.home() / 'Projects/techscript-video-pipeline'))
parser.add_argument('--ep', required=True)
parser.add_argument('--voice', default='中文男', help='SFT speaker: 中文男/中文女/英文男/英文女/...')
parser.add_argument('--model', default=str(Path.home() / 'Projects/cosyvoice_local/pretrained_models/CosyVoice-300M-SFT'))
args = parser.parse_args()

ep_dir = Path(args.project_root) / 'episodes' / args.ep
script_path = ep_dir / 'script.md'
out_dir = ep_dir / 'audio' / 'voiceover'
out_dir.mkdir(parents=True, exist_ok=True)

if not script_path.exists():
    print(f'❌ {script_path} not found'); sys.exit(1)

text = script_path.read_text(encoding='utf-8')
# 解析 ## sNN ... ## sNN
segments = re.findall(r'^##\s+(s\d+)\s*\n(.*?)(?=^##\s+s\d+|\Z)', text, re.MULTILINE | re.DOTALL)
if not segments:
    print('❌ no ## sNN segments found'); sys.exit(1)

print(f'📋 {len(segments)} segments to synthesize')
print(f'🎤 voice = {args.voice}')

print('Loading CosyVoice model...')
cv = AutoModel(model_dir=args.model)
print(f'Available speakers: {cv.list_available_spks()}')

for seg_id, content in segments:
    content = content.strip()
    if not content:
        continue
    out_wav = out_dir / f'{args.ep}_{seg_id}.wav'
    out_mp3 = out_dir / f'{args.ep}_{seg_id}.mp3'
    print(f'\n→ {seg_id}: {content[:40]}...')

    for i, chunk in enumerate(cv.inference_sft(content, args.voice, stream=False)):
        torchaudio.save(str(out_wav), chunk['tts_speech'], cv.sample_rate)
        break  # 取第一个 chunk

    # 转 mp3
    subprocess.run([
        'ffmpeg', '-y', '-i', str(out_wav),
        '-ar', '44100', '-ac', '1', '-b:a', '128k',
        str(out_mp3)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out_wav.unlink()

    # 报告时长
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(out_mp3)],
        capture_output=True, text=True
    )
    print(f'   ✓ {out_mp3.name}  duration={probe.stdout.strip()}s')

print('\n🎉 done')
