#!/usr/bin/env python3
"""CosyVoice runner — runs INSIDE ~/Projects/cosyvoice_local/.venv (has torch+torchaudio).

Modes:
  sft       — fixed speakers (中文男/中文女)
  zero_shot — clone voice from a prompt wav
  instruct3 — zero-shot + instruct prompt (e.g. "用欢快阳光的语气说<|endofprompt|>")

Output: writes .wav to OUT_WAV (caller can convert to mp3 with ffmpeg).
"""
from __future__ import annotations
import sys, json
from pathlib import Path

COSY = Path.home() / "Projects/cosyvoice_local"
sys.path.insert(0, str(COSY))
sys.path.insert(0, str(COSY / "third_party/Matcha-TTS"))

import torchaudio  # type: ignore
from cosyvoice.cli.cosyvoice import AutoModel  # type: ignore


def main():
    if len(sys.argv) != 2:
        print("usage: cosyvoice_runner.py <args.json>"); sys.exit(2)
    args = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    model_dir = args["model_dir"]
    text = args["text"]
    mode = args.get("mode", "sft")
    out_wav = args["out_wav"]
    speaker = args.get("speaker", "中文男")
    prompt_wav = args.get("prompt_wav")
    prompt_text = args.get("prompt_text", "")
    instruct = args.get("instruct", "")  # e.g. "用欢快阳光的语气说<|endofprompt|>"
    speed = float(args.get("speed", 1.0))

    print(f"[cosyvoice] loading {model_dir}", flush=True)
    model = AutoModel(model_dir=model_dir)

    if mode == "sft":
        gen = model.inference_sft(text, speaker, stream=False, speed=speed)
    elif mode == "zero_shot":
        # CV3 needs system prompt + actual prompt_text matching the prompt_wav
        sys_prompt = args.get("system_prompt", "You are a helpful assistant.<|endofprompt|>")
        full_prompt = sys_prompt + prompt_text
        gen = model.inference_zero_shot(text, full_prompt, prompt_wav, stream=False, speed=speed)
    elif mode == "instruct3":
        # CV3 instruct: system_prompt replaced by instruct
        # e.g. instruct = "用欢快阳光的语气说<|endofprompt|>"
        sys_prompt = instruct if instruct else "You are a helpful assistant.<|endofprompt|>"
        full_prompt = sys_prompt + prompt_text
        gen = model.inference_zero_shot(text, full_prompt, prompt_wav, stream=False, speed=speed)
    else:
        raise ValueError(f"unknown mode: {mode}")

    for r in gen:
        torchaudio.save(out_wav, r["tts_speech"], model.sample_rate)
        print(f"[cosyvoice] saved {out_wav} ({r['tts_speech'].shape[-1]/model.sample_rate:.2f}s)", flush=True)
        return
    raise RuntimeError("no audio produced")


if __name__ == "__main__":
    main()
