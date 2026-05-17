"""TTS base + registry."""
from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, List

_REGISTRY: Dict[str, "TTSProvider"] = {}


def register(name: str):
    def deco(cls):
        _REGISTRY[name.lower()] = cls
        cls.name = name
        return cls
    return deco


def get_provider(name: str) -> "TTSProvider":
    key = name.lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown TTS provider: {name}. Known: {list(_REGISTRY)}")
    return _REGISTRY[key]()


def list_providers() -> List[str]:
    return sorted(_REGISTRY.keys())


class TTSProvider(abc.ABC):
    name: str = ""
    default_voice: str = ""
    # voice_id -> human description
    voices: Dict[str, str] = {}

    @abc.abstractmethod
    def synth(self, text: str, out_path: Path, voice: str | None = None, **kwargs) -> Path:
        """Synthesize `text` -> out_path (.mp3). Returns out_path."""
        ...

    def available(self) -> tuple[bool, str]:
        """Return (ok, reason)."""
        return True, "ok"
