"""ElevenLabs (paid, multilingual v2 best quality)."""
from __future__ import annotations
import os
from pathlib import Path
from .base import TTSProvider, register


@register("elevenlabs")
class ElevenLabsTTS(TTSProvider):
    default_voice = "21m00Tcm4TlvDq8ikWAM"  # Rachel (auto-detects zh)
    voices = {
        "21m00Tcm4TlvDq8ikWAM": "🌟 Rachel — calm 多语女声",
        "CwhRBWXzGAHq8TQ4Fs17": "💼 Roger — 沉稳男声",
        "EXAVITQu4vr4xnSDxMaL": "✨ Bella — 温暖女声",
        "TxGEqnHWrfWFTfGW9XjX": "📢 Josh — 年轻男声",
    }

    def available(self):
        if not os.getenv("ELEVENLABS_API_KEY"):
            return False, "ELEVENLABS_API_KEY missing in env"
        return True, "ok"

    def synth(self, text: str, out_path: Path, voice: str | None = None,
              model_id: str = "eleven_multilingual_v2", **kwargs) -> Path:
        import requests
        key = os.environ["ELEVENLABS_API_KEY"]
        voice = voice or self.default_voice
        out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        r = requests.post(url, headers={
            "xi-api-key": key, "Content-Type": "application/json",
            "accept": "audio/mpeg",
        }, json={
            "text": text, "model_id": model_id,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.7, "style": 0.3},
        }, timeout=120)
        r.raise_for_status()
        out_path.write_bytes(r.content)
        return out_path
