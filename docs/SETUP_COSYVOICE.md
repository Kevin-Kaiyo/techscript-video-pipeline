# CosyVoice Setup

CosyVoice is optional. Use Edge TTS for the fastest reproducible setup, and use CosyVoice only when you need local offline TTS or voice cloning.

## Recommended Default

For most development work:

```bash
python pipeline/tts_cli.py --provider edge --voice zh-CN-YunjianNeural --ep demo-industry
```

Edge TTS does not need an API key and is much faster on a small Mac.

## Local CosyVoice Layout

This project expects CosyVoice to live outside the repository:

```text
~/Projects/cosyvoice_local/
├── .venv/
├── CosyVoice source files
└── pretrained_models/
```

Do not commit CosyVoice models, virtual environments, or generated voice samples to this repository.

## Install Sketch

```bash
git clone https://github.com/FunAudioLLM/CosyVoice ~/Projects/cosyvoice_local
cd ~/Projects/cosyvoice_local
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the model required by your local CosyVoice version. Model commands change over time, so check the upstream CosyVoice README before treating the command below as authoritative:

```bash
python -c "from modelscope import snapshot_download; snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B', local_dir='pretrained_models/Fun-CosyVoice3-0.5B')"
```

## Voice Clone Inputs

Voice samples are personal data. Keep raw samples local:

```text
voices/<speaker>/prompt_raw.wav      # ignored by git
voices/<speaker>/prompt_text.txt     # safe text transcript, can be committed
```

## Performance Notes

On an 8GB Mac mini, CPU-only CosyVoice can be several times slower than real time. Use Edge TTS while iterating, then switch to CosyVoice for final voice experiments.

## Current Status

CosyVoice support exists through the TTS provider abstraction, but it is not part of the minimum fresh-clone path. A fresh clone should work with Edge TTS first.
