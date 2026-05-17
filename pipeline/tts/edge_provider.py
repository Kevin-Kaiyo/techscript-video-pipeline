"""Microsoft Edge-TTS (free, online).

Voices: zh-CN-* — Yunxi (sunshine lively male), Yunyang (professional), Xiaoxiao (warm female), etc.
Rate / pitch adjustable.
"""
from __future__ import annotations
import asyncio
from pathlib import Path
import shutil
from .base import TTSProvider, register


@register("edge")
class EdgeTTS(TTSProvider):
    default_voice = "zh-CN-YunxiNeural"
    voices = {
        "zh-CN-YunxiNeural":   "🌞 云希 — 男·阳光活泼 (推荐 default)",
        "zh-CN-YunjianNeural": "💪 云健 — 男·激情解说",
        "zh-CN-YunyangNeural": "📰 云扬 — 男·专业可靠",
        "zh-CN-YunxiaNeural":  "🧒 云夏 — 男·可爱卡通",
        "zh-CN-XiaoxiaoNeural":"🌸 晓晓 — 女·温暖叙事",
        "zh-CN-XiaoyiNeural":  "✨ 晓伊 — 女·活泼少女",
    }

    def available(self):
        if shutil.which("edge-tts") is None:
            try:
                import edge_tts  # noqa: F401
            except Exception:
                return False, "pip install edge-tts (or use venv-tts)"
        return True, "ok"

    def synth(self, text: str, out_path: Path, voice: str | None = None,
              rate: str = "+0%", pitch: str = "+0Hz", **kwargs) -> Path:
        import edge_tts  # type: ignore
        voice = voice or self.default_voice
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        async def _run():
            comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await comm.save(str(out_path))

        asyncio.run(_run())
        return out_path
