# Voice Samples

This directory stores voice prompt samples for CosyVoice zero-shot cloning.

**The actual `.wav` files are NOT committed** (listed in `.gitignore` to protect personal voice data).

## How to use

1. Record a 15–30s clean voice sample (quiet room, mono, any format)
2. Convert: `ffmpeg -i your_sample.m4a -af "highpass=f=80,loudnorm=I=-18:LRA=7" -ar 24000 -ac 1 voices/kevin/prompt_raw.wav`
3. Update `voices/kevin/prompt_text.txt` with the transcript of your recording
4. Run: `python pipeline/tts_cli.py --provider cosyvoice-clone --voice voices/kevin/prompt_raw.wav --text "测试" --out /tmp/test.mp3`

## File structure expected

```
voices/
└── <speaker_name>/
    ├── prompt_raw.wav        # NOT committed (add to .gitignore)
    ├── prompt_text.txt       # transcript of prompt_raw.wav ✅ committed
    └── README.md             # this file ✅ committed
```
