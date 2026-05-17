"""CosyVoice (local) — runs the runner inside ~/Projects/cosyvoice_local/.venv via subprocess.

Three providers exposed:
  - cosyvoice (SFT, fixed 中文男/中文女, fast, no clone)
  - cosyvoice-clone (CosyVoice3 zero-shot, needs prompt_wav + prompt_text)
  - cosyvoice-instruct (CosyVoice3 zero-shot + instruct, e.g. "用欢快阳光的语气说")
"""
from __future__ import annotations
import json, os, subprocess, tempfile
from pathlib import Path
from .base import TTSProvider, register

COSY_ROOT = Path.home() / "Projects/cosyvoice_local"
COSY_VENV_PY = COSY_ROOT / ".venv/bin/python"
SFT_MODEL = COSY_ROOT / "pretrained_models/CosyVoice-300M-SFT"
CV3_MODEL = COSY_ROOT / "pretrained_models/Fun-CosyVoice3-0.5B"
RUNNER = Path(__file__).parent / "cosyvoice_runner.py"


def _run_runner(args: dict, timeout=600):
    """Invoke runner inside cosyvoice venv; produce wav then convert to caller's mp3."""
    out_mp3 = Path(args.pop("out_mp3"))
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp_wav = tf.name
    args["out_wav"] = tmp_wav
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tj:
        json.dump(args, tj, ensure_ascii=False); tj.flush()
        argjson = tj.name
    try:
        env = os.environ.copy()
        env.pop("PYTHONHOME", None); env.pop("PYTHONPATH", None)
        proc = subprocess.run(
            [str(COSY_VENV_PY), str(RUNNER), argjson],
            cwd=str(COSY_ROOT), env=env, timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"cosyvoice runner failed:\n{proc.stdout.decode('utf-8','replace')[-2000:]}")
        # wav -> mp3
        subprocess.run(["ffmpeg","-y","-i",tmp_wav,"-b:a","128k",str(out_mp3)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        try: os.unlink(tmp_wav)
        except OSError: pass
        try: os.unlink(argjson)
        except OSError: pass
    return out_mp3


@register("cosyvoice")
class CosyVoiceSFT(TTSProvider):
    """Quick fixed-speaker SFT (CosyVoice-300M-SFT)."""
    default_voice = "中文男"
    voices = {"中文男": "🎤 CV-SFT 中文男 (本地, 快)", "中文女": "🎤 CV-SFT 中文女 (本地, 快)"}

    def available(self):
        if not COSY_VENV_PY.exists(): return False, f"missing {COSY_VENV_PY}"
        if not SFT_MODEL.exists(): return False, f"missing {SFT_MODEL}"
        return True, "ok"

    def synth(self, text, out_path, voice=None, speed=1.0, **kw):
        return _run_runner({
            "mode": "sft", "model_dir": str(SFT_MODEL),
            "text": text, "speaker": voice or self.default_voice,
            "speed": speed, "out_mp3": str(out_path),
        })


@register("cosyvoice-clone")
class CosyVoice3Clone(TTSProvider):
    """CosyVoice3 zero-shot clone. Voice = path to a prompt wav (15-30s ideal)."""
    default_voice = ""  # caller must pass prompt wav path
    voices = {"<wav_path>": "🧬 CV3 zero-shot 克隆 — voice 参数 = prompt wav 路径"}

    def available(self):
        if not COSY_VENV_PY.exists(): return False, f"missing {COSY_VENV_PY}"
        if not CV3_MODEL.exists(): return False, f"missing {CV3_MODEL}"
        return True, "ok (传 voice=prompt.wav, kwargs.prompt_text=文本)"

    def synth(self, text, out_path, voice=None, prompt_text="", speed=1.0, **kw):
        if not voice or not Path(voice).exists():
            raise ValueError(f"cosyvoice-clone needs voice=<prompt_wav_path>, got: {voice}")
        return _run_runner({
            "mode": "zero_shot", "model_dir": str(CV3_MODEL),
            "text": text, "prompt_wav": str(voice), "prompt_text": prompt_text,
            "speed": speed, "out_mp3": str(out_path),
        })


@register("cosyvoice-instruct")
class CosyVoice3Instruct(TTSProvider):
    """CosyVoice3 zero-shot + instruct prompt. voice=prompt wav path."""
    default_voice = ""
    voices = {"<wav_path>": "✨ CV3 克隆 + 指令 — voice=prompt wav, kwargs.instruct=指令"}

    def available(self):
        if not COSY_VENV_PY.exists(): return False, f"missing {COSY_VENV_PY}"
        if not CV3_MODEL.exists(): return False, f"missing {CV3_MODEL}"
        return True, "ok (voice=prompt.wav, kwargs.instruct='用欢快阳光语气说<|endofprompt|>')"

    def synth(self, text, out_path, voice=None, prompt_text="", instruct="", speed=1.0, **kw):
        if not voice or not Path(voice).exists():
            raise ValueError(f"cosyvoice-instruct needs voice=<prompt_wav_path>, got: {voice}")
        return _run_runner({
            "mode": "instruct3", "model_dir": str(CV3_MODEL),
            "text": text, "prompt_wav": str(voice),
            "prompt_text": prompt_text, "instruct": instruct,
            "speed": speed, "out_mp3": str(out_path),
        })
