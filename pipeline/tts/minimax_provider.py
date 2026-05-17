"""MiniMax T2A (海螺) — placeholder, requires paid quota."""
from __future__ import annotations
import os
from pathlib import Path
from .base import TTSProvider, register


@register("minimax")
class MiniMaxTTS(TTSProvider):
    default_voice = "male-qn-qingse"
    voices = {
        "male-qn-qingse":  "💼 青涩青年 — 男",
        "male-qn-jingying":"🎯 精英青年 — 男",
        "male-qn-badao":   "💪 霸道总裁 — 男",
        "presenter_male":  "📺 男主持人",
        "presenter_female":"📺 女主持人",
        "audiobook_male_1":"📖 男有声书演员1",
        "audiobook_female_1":"📖 女有声书演员1",
    }

    def available(self):
        if not os.getenv("MINIMAX_API_KEY"):
            return False, "MINIMAX_API_KEY missing"
        # Kevin 说账户没钱，所以默认 disabled
        return False, "⚠️ MiniMax 账户余额不足 (Kevin 标记)，已预留接口"

    def synth(self, text, out_path, voice=None, group_id=None, **kw):
        import requests, json
        key = os.environ["MINIMAX_API_KEY"]
        gid = group_id or os.getenv("MINIMAX_GROUP_ID", "")
        voice = voice or self.default_voice
        out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://api.minimaxi.chat/v1/t2a_v2?GroupId={gid}"
        r = requests.post(url, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        }, json={
            "model": "speech-02-hd",
            "text": text,
            "stream": False,
            "voice_setting": {"voice_id": voice, "speed": 1.0, "vol": 1.0, "pitch": 0},
            "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3"},
        }, timeout=120)
        r.raise_for_status()
        data = r.json()
        audio_hex = data["data"]["audio"]
        out_path.write_bytes(bytes.fromhex(audio_hex))
        return out_path
