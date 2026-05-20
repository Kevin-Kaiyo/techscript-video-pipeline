# 架构设计

## 系统概览

```
┌─────────────────────────────────────────────────────────────┐
│                    TechScript Video Pipeline                  │
├─────────────┬──────────────────┬──────────────────┬─────────┤
│  内容层      │   渲染层          │   音频层          │  合成层 │
│  script.md  │  HyperFrames     │  TTS Providers   │ FFmpeg  │
│  storyboard │  (GSAP+HTML+CDP) │  Edge / CV3      │ compose │
│             │  Manim           │  ElevenLabs etc  │         │
└─────────────┴──────────────────┴──────────────────┴─────────┘
```

## 目录结构

```
techscript-video-pipeline/
│
├── episodes/                    # 每集独立，结构一致
│   └── <ep-name>/
│       ├── script.md            # 文案脚本（## sNN 分段）
│       ├── audio_schedule.json  # 音画对齐时间表（自动生成）
│       ├── animations/
│       │   └── hyperframes/     # HTML+GSAP 信息图动画源码
│       │       └── index.html
│       ├── audio/
│       │   └── voiceover/       # TTS 生成的 mp3 文件
│       ├── subtitles/           # SRT 字幕（可选）
│       └── output/              # 最终 MP4（不提交到 git）
│
├── pipeline/                    # 工具脚本（核心）
│   ├── tts/                     # TTS 抽象层（Python 包）
│   │   ├── base.py              # Provider ABC + registry
│   │   ├── edge_provider.py     # Microsoft Edge TTS（推荐）
│   │   ├── cosyvoice_provider.py# CosyVoice SFT / 3 zero-shot
│   │   ├── cosyvoice_runner.py  # CosyVoice venv 隔离 runner
│   │   ├── elevenlabs_provider.py
│   │   ├── minimax_provider.py
│   │   └── google_provider.py
│   ├── tts_cli.py               # 统一 TTS CLI 入口
│   ├── render_cdp_resumable.mjs # CDP 渲染器（断点续传）
│   ├── compose_audio.mjs        # 音轨合成（schedule → FFmpeg）
│   ├── auto_schedule.mjs        # 自动生成音画 schedule
│   ├── build_episode.sh         # 全流程构建脚本
│   └── preview_shots.mjs        # 关键帧预览工具
│
├── shared/
│   └── brand/                   # 全局配置（颜色/字体/TTS/视频规格）
│
├── voices/                      # 声音克隆样本（wav 不提交）
│   └── <speaker>/
│       ├── prompt_raw.wav       # .gitignore 中
│       └── prompt_text.txt      # 样本文本（提交）
│
└── docs/                        # 项目文档
```

## 核心数据流

### HyperFrames 渲染流

```
script.md
    │
    ▼
index.html (GSAP timeline)
    │
    ├─ HTTP Server (python3 -m http.server :18234)
    │
    ▼
render_cdp_resumable.mjs
    │  Chrome CDP → 截图 → JPEG
    │  断点续传（frame_NNNNN.jpg 已存在则跳过）
    ▼
/tmp/<ep>_frames/frame_NNNNN.jpg  (fps × duration; default from shared/brand/video.json)
    │
    ▼
FFmpeg → <ep>_silent.mp4
    │
    ├─ compose_audio.mjs
    │      + audio_schedule.json
    │      + voiceover/*.mp3
    ▼
output/<ep>_full.mp4
```

### Manim 渲染流

```
script.md
    │
    ├─ tts_cli.py → audio/voiceover/*.mp3
    ├─ auto_schedule.mjs → audio_schedule.json
    │
    ▼
pipeline/manim/<scene>.py
    │  Python / Manim scene
    ▼
Manim renderer
    │  Cairo/OpenGL style scientific animation
    ▼
episodes/<ep>/output/<ep>_silent.mp4
    │
    ├─ compose_audio.mjs
    ▼
episodes/<ep>/output/<ep>_full.mp4
```

### TTS 配音流

```
script.md
    │  (## sNN 分段解析)
    ▼
tts_cli.py --provider edge --voice zh-CN-YunjianNeural --ep <ep>
    │
    ▼
pipeline/tts/<provider>_provider.py
    │  synth(text, out_path, voice, **kwargs)
    ▼
audio/voiceover/<ep>_sNN.mp3
    │
    ▼
auto_schedule.mjs  (ffprobe 测段长)
    │
    ▼
audio_schedule.json  { tracks: [{file, start_ms}...] }
```

## 关键设计决策

### 1. CDP 渲染 vs Puppeteer/Playwright

使用原生 Chrome DevTools Protocol，避免 Playwright 的 headless 模式对 GSAP 的兼容性问题。  
断点续传设计使大视频（>500帧）可以分批完成，不怕 OOM。

### 2. TTS 抽象层设计

```python
class TTSProvider(ABC):
    default_voice: str
    voices: dict[str, str]
    
    def available(self) -> tuple[bool, str]: ...
    def synth(self, text, out_path, voice=None, **kwargs) -> Path: ...
```

所有 provider 通过装饰器 `@register("name")` 注册，`tts_cli.py` 统一入口，切换 provider 只需改一个参数。

### 3. CosyVoice 隔离运行

CosyVoice 依赖 PyTorch (Python 3.11 + torch 2.3)，与项目主 venv 隔离。  
通过 subprocess 调用 `cosyvoice_runner.py`，传 JSON 参数，输出 WAV 后由主进程转 MP3。

### 4. 内容类型 × 渲染工具

不同技术内容有不同的最优渲染工具：

| 场景 | 工具 | 原因 |
|------|------|------|
| 技术/算法/工艺动作 | Manim | 数学精确，几何动画，制造过程表达强 |
| 产业/上下游 | HyperFrames | 流程图、卡片、高亮动效灵活 |
| 设备/材料/供应链 | HyperFrames | 多节点关系、对比和分类表达清晰 |
| 数据/图表 | HyperFrames | SVG 动画柱状图/趋势线/饼图 |

### Remotion Position

Remotion is not a dependency today. It is technically closer to HyperFrames than to Manim:

- HyperFrames: HTML/CSS/GSAP in Chrome, captured through CDP.
- Remotion: React components in Chrome, captured and composed through the Remotion toolchain.
- Manim: Python scene graph rendered by the Manim engine, then composed with FFmpeg.

If HyperFrames becomes hard to maintain, Remotion is the likely upgrade path for the browser-rendered information-graphics line. It is not a replacement for Manim.
