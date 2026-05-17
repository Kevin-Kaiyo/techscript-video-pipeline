# TTS Provider 对比与使用

## Provider 总览

| Provider | 免费 | 中文质量 | 延迟 | 离线 | 克隆 |
|----------|------|---------|------|------|------|
| Edge TTS | ✅ | ⭐⭐⭐⭐ | 快 | ❌ | ❌ |
| CosyVoice SFT | ✅ | ⭐⭐⭐ | 中 | ✅ | ❌ |
| CosyVoice3 | ✅ | ⭐⭐⭐⭐ | 慢 | ✅ | ✅ |
| ElevenLabs | 限额 | ⭐⭐⭐⭐⭐ | 快 | ❌ | ✅ |
| MiniMax | 付费 | ⭐⭐⭐⭐⭐ | 快 | ❌ | ❌ |
| Google TTS | 付费 | ⭐⭐⭐⭐ | 快 | ❌ | ❌ |

## 推荐选择

- **日常开发/快速迭代**：Edge TTS `zh-CN-YunjianNeural`（激情解说男，免费）
- **发布质量**：ElevenLabs（需付费）或 CosyVoice3 声音克隆
- **完全离线**：CosyVoice3

## Edge TTS 音色列表（中文）

```python
# 运行查看所有可用音色
python pipeline/tts_cli.py --list
```

推荐男声：
- `zh-CN-YunjianNeural` — 激情解说，适合科技内容
- `zh-CN-YunxiNeural` — 阳光活泼，适合科普
- `zh-CN-YunyangNeural` — 专业可靠，适合正式内容

## 声音克隆（CosyVoice3）

```python
from pipeline.tts import get_provider

# 注册声音
p = get_provider("cosyvoice-clone")
p.synth(
    "要合成的文本内容",
    "output.mp3",
    voice="voices/your_name/prompt_raw.wav",
    prompt_text="你的 prompt wav 里说了什么",
)

# 带情绪指令
p2 = get_provider("cosyvoice-instruct")
p2.synth(
    "要合成的文本内容",
    "output.mp3",
    voice="voices/your_name/prompt_raw.wav",
    prompt_text="你的 prompt wav 里说了什么",
    instruct="用欢快阳光的语气说<|endofprompt|>",
)
```
