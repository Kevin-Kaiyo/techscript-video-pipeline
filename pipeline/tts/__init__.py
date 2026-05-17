"""TTS provider abstraction.

Each provider exposes the same `synth(text, out_path, voice, **kw)` API.
Provider names are looked up case-insensitively.
"""
from .base import TTSProvider, register, get_provider, list_providers  # noqa
from . import edge_provider, cosyvoice_provider, elevenlabs_provider, minimax_provider, google_provider  # noqa: F401
# cosyvoice_provider registers: cosyvoice (SFT), cosyvoice-clone (CV3 zero-shot), cosyvoice-instruct (CV3 instruct)
