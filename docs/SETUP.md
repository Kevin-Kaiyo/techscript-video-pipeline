# 环境搭建指南

## 基础环境

### 必须安装

```bash
# Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 基础工具
brew install ffmpeg node python@3.11 git

# Google Chrome（用于 CDP 渲染，必须）
# 从 https://www.google.com/chrome/ 下载安装
```

### Python 环境（TTS）

```bash
cd techscript-video-pipeline
python3 -m venv .venv-tts
source .venv-tts/bin/activate
pip install edge-tts requests tabulate
```

### Node 环境（渲染器）

```bash
# 全局安装 ws（CDP 渲染依赖）
cd /tmp && npm install ws
```

---

## TTS Provider 配置

### Edge TTS（推荐，免费，无需 Key）

```bash
pip install edge-tts
# 测试
edge-tts --voice zh-CN-YunjianNeural --text "测试" --write-media /tmp/test.mp3
```

### ElevenLabs（付费，高质量）

```bash
# .env 中设置
ELEVENLABS_API_KEY=your_key_here
```

### MiniMax（付费，中文优秀）

```bash
MINIMAX_API_KEY=your_key_here
MINIMAX_GROUP_ID=your_group_id
```

### Google Cloud TTS（需开通 TTS API）

```bash
GOOGLE_API_KEY=your_key_here
# 在 GCP Console 开启 Cloud Text-to-Speech API
```

---

## CosyVoice（本地离线 TTS / 声音克隆）

详见 [docs/SETUP_COSYVOICE.md](SETUP_COSYVOICE.md)

简版：
```bash
git clone https://github.com/FunAudioLLM/CosyVoice ~/Projects/cosyvoice_local
cd ~/Projects/cosyvoice_local
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 下载模型（约 2GB）
python -c "from modelscope import snapshot_download; snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir='pretrained_models/Fun-CosyVoice3-0.5B')"
```

---

## 常见问题

### Q: Chrome 渲染时字体加载失败？

动画 HTML 使用了 Google Fonts CDN。离线环境需要在 HTML 中内嵌字体或使用系统字体。

### Q: Mac 8GB 内存渲染 OOM？

减小 batch 大小：
```bash
# 将 400 改为 200
node pipeline/render_cdp_resumable.mjs 24 40 /tmp/frames demo-ep \
  "http://localhost:18234/index.html" 200
```

### Q: `ffmpeg: command not found`？

```bash
brew install ffmpeg
```

### Q: CosyVoice 速度很慢？

CPU-only 模式 RTF ≈ 4（即 10s 音频需 40s 推理）。这是正常的，Mac 无 CUDA。  
对于快速迭代，推荐先用 Edge TTS，完稿后再换 CosyVoice。
