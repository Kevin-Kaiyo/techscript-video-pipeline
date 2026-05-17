<div align="center">

# 🎬 TechScript Video Pipeline

**把技术文章变成科普视频的开源工作流**  
*An open-source pipeline to turn technical content into explainer videos*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Node 20+](https://img.shields.io/badge/Node-20%2B-green)](https://nodejs.org)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS%20M-lightgrey)](https://apple.com)

[📖 文档](#文档) · [🚀 快速开始](#快速开始) · [🎞️ 示例](#示例) · [🗺️ 路线图](#路线图)

</div>

---

## 项目简介

TechScript Video Pipeline 是一套**本地优先、可复刻**的技术讲解视频生成工作流。  
它把「写一篇技术文章」这件事，标准化地转化成「一段有动画、有配音、有字幕的科普短视频」。

### 核心能力

| 能力 | 工具 | 说明 |
|------|------|------|
| 动画渲染（产业/数据类） | HyperFrames (GSAP + HTML) | 浏览器动画 → CDP 截帧 → MP4 |
| 动画渲染（技术/算法类） | Manim *(计划中)* | 数学几何动画，3Blue1Brown 风格 |
| 多 backend 配音 | Edge-TTS / CosyVoice3 / ElevenLabs | 可插拔 TTS 抽象层 |
| 声音克隆 | CosyVoice3 zero-shot | 本地离线，15s 样本即可 |
| 音画对齐 | ffprobe + auto_schedule.mjs | 自动测段长、生成 schedule |
| 视频合成 | FFmpeg | 画面 + 多轨配音 → 最终 MP4 |

### 内容类型 × 工具选择

```
技术/算法类  ──▶  Manim *(计划中)*  (数学推导、几何原理)
产业/上下游  ──▶  HyperFrames       (流程图、产业链、公司对比)
数据/图表类  ──▶  HyperFrames       (柱状图、趋势线、饼图)
```

---

## 快速开始

### 环境要求

- macOS（Apple Silicon 优化，M1/M2/M3 均可）
- Python 3.9+
- Node.js 20+
- Google Chrome（用于 CDP 渲染）
- FFmpeg

### 1. 克隆项目

```bash
git clone https://github.com/Kevin-Kaiyo/microled-science-video.git
cd microled-science-video
```

### 2. 安装 Python 依赖

```bash
python3 -m venv .venv-tts
source .venv-tts/bin/activate
pip install edge-tts requests tabulate
```

### 3. 安装 Node 依赖（仅渲染器需要）

```bash
cd /tmp && npm install ws
```

### 4. （可选）安装 CosyVoice（本地 TTS）

```bash
# 参考 docs/SETUP_COSYVOICE.md
```

### 5. 配置 API Keys（可选）

```bash
cp .env.example .env
# 编辑 .env，填入需要的 key（edge-tts 不需要 key）
```

### 6. 生成一集视频

```bash
# 查看示例集数
ls episodes/

# 生成配音
python pipeline/tts_cli.py --provider edge --voice zh-CN-YunjianNeural --ep demo-industry

# 自动对齐 schedule
node pipeline/auto_schedule.mjs episodes/demo-industry

# 启动 HTTP 渲染服务（新终端）
cd episodes/demo-industry/animations/hyperframes && python3 -m http.server 18234

# 渲染帧
node pipeline/render_cdp_resumable.mjs 24 40 /tmp/demo-industry_frames demo-industry \
  "http://localhost:18234/index.html" 400

# 合成最终视频
bash pipeline/build_episode.sh demo-industry
```

---

## 示例

本项目内置三个示例集数，覆盖三种内容类型：

| 集数 | 类型 | 主题 | 时长 |
|------|------|------|------|
| `demo-tech` | 技术/工艺 | Micro LED 巨量转移 | ~45s |
| `demo-industry` | 产业链 | Micro LED 上中下游全景 | ~40s |
| `demo-data` | 数据图表 | 全球显示市场增长 | ~36s |

---

## 文档

- [🏗️ 架构设计](docs/ARCHITECTURE.md) — 系统组件与数据流
- [🔄 工作流详解](docs/WORKFLOW.md) — 从文章到视频的完整步骤
- [⚙️ 环境搭建](docs/SETUP.md) — 安装、配置、常见问题
- [🔊 TTS 配置](docs/TTS.md) — 各 backend 对比与使用方法
- [🤝 贡献指南](CONTRIBUTING.md)

---

## 路线图

- [x] HyperFrames 渲染管线（CDP 断点续传）
- [x] 多 backend TTS 抽象层（Edge / CosyVoice3 / ElevenLabs / MiniMax / Google）
- [x] 音画自动对齐（ffprobe → auto_schedule）
- [x] 声音克隆（CosyVoice3 zero-shot，本地离线）
- [ ] Manim 技术类动画模板
- [ ] 字幕自动生成（Whisper）
- [ ] 一键生成脚本（LLM → script.md）
- [ ] GitHub Actions 自动化构建

---

## 许可证

代码部分：[MIT License](LICENSE)

**注意**：本项目使用 [GSAP](https://gsap.com/licensing/) 进行动画渲染。  
GSAP 在**非商业用途**下免费使用。如需商业部署，请购买 GSAP 商业授权。

详见 [NOTICE](NOTICE)。

---

<div align="center">
Made with ❤️ by <a href="https://github.com/Kevin-Kaiyo">Kaiyo Nan</a> · <a href="https://kaiyo-blog.pages.dev">Blog</a>
</div>
