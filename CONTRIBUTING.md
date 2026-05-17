# 贡献指南

## 欢迎贡献

这个项目的目标是：**让任何人都能用 AI + 自动化工具，制作出专业级技术讲解视频。**

你可以通过以下方式贡献：

## 可以贡献的内容

### 动画原语（高价值）
- 新的 HyperFrames 场景模板（流程图、时间轴、对比表等）
- Manim 技术类动画模板
- 更好的 SVG 图标库集成

### TTS 改进
- 新的 TTS provider（如 OpenAI TTS、Azure TTS）
- 字幕自动同步

### 工具链
- 自动从文章生成 script.md（LLM 接口）
- Whisper 字幕自动生成
- Docker 环境（方便非 macOS 用户）

## 如何贡献

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feat/your-feature`
3. 提交更改：`git commit -m "feat: 描述"`
4. 推送分支：`git push origin feat/your-feature`
5. 发起 Pull Request

## 开发规范

### 新增 TTS Provider

继承 `pipeline/tts/base.py` 中的 `TTSProvider` ABC：

```python
from .base import TTSProvider, register

@register("your-provider-name")
class YourTTS(TTSProvider):
    default_voice = "default-voice-id"
    voices = {"voice-id": "描述"}
    
    def available(self) -> tuple[bool, str]:
        # 检查 API key / 本地模型是否可用
        ...
    
    def synth(self, text, out_path, voice=None, **kwargs) -> Path:
        # 调用 TTS API，保存到 out_path
        ...
```

然后在 `pipeline/tts/__init__.py` 中 import 你的模块。

### 新增 HyperFrames 场景模板

在 `pipeline/templates/` 下创建 `scene_<type>.html`，遵循规范：
- `data-composition-id` 必须唯一
- 使用 inline SVG 而非 emoji
- `window.__timelines[compId] = tl` 必须设置

## 许可证说明

提交代码即表示你同意将代码以 MIT License 授权。  
注意 GSAP 的非商业限制（见 NOTICE）。
