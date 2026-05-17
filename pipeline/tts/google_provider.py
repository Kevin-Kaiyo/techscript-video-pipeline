"""Google Cloud TTS (Chirp 3 HD / Neural2 / WaveNet 中文音色).

Uses GOOGLE_API_KEY (REST endpoint, no SDK needed). Optional, predicted to work
if Kevin's GOOGLE_API_KEY has TTS API enabled in the linked project.
"""
from __future__ import annotations
import os, base64
from pathlib import Path
from .base import TTSProvider, register


@register("google")
class GoogleTTS(TTSProvider):
    default_voice = "cmn-CN-Wavenet-B"
    voices = {
        "cmn-CN-Wavenet-A": "📻 普通话 — 女 (WaveNet-A)",
        "cmn-CN-Wavenet-B": "📻 普通话 — 男 (WaveNet-B)",
        "cmn-CN-Wavenet-C": "📻 普通话 — 男 (WaveNet-C)",
        "cmn-CN-Wavenet-D": "📻 普通话 — 女 (WaveNet-D)",
        "cmn-CN-Neural2-A": "🌟 普通话 — 女 (Neural2-A，更自然)",
        "cmn-CN-Neural2-B": "🌟 普通话 — 男 (Neural2-B，更自然)",
        "cmn-CN-Neural2-C": "🌟 普通话 — 男 (Neural2-C，更自然)",
        "cmn-CN-Neural2-D": "🌟 普通话 — 女 (Neural2-D，更自然)",
    }

    def available(self):
        if not os.getenv("GOOGLE_API_KEY"):
            return False, "GOOGLE_API_KEY missing"
        return True, "ok (需要在该 GCP project 启用 Cloud Text-to-Speech API)"

    def synth(self, text, out_path, voice=None, speaking_rate=1.0, pitch=0.0, **kw):
        import requests
        key = os.environ["GOOGLE_API_KEY"]
        voice = voice or self.default_voice
        lang = "-".join(voice.split("-")[:2])  # "cmn-CN"
        out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}"
        r = requests.post(url, json={
            "input": {"text": text},
            "voice": {"languageCode": lang, "name": voice},
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": speaking_rate, "pitch": pitch},
        }, timeout=60)
        r.raise_for_status()
        out_path.write_bytes(base64.b64decode(r.json()["audioContent"]))
        return out_path
