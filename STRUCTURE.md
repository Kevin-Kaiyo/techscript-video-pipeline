# 项目结构（v2 — 2026-05-17 重组）

```
techscript-video-pipeline/
├── episodes/
│   └── ep01/                              # 每集独立目录
│       ├── script.md                      # 文案脚本
│       ├── storyboard.md                  # 分镜
│       ├── audio/
│       │   ├── voiceover/                 # 6段配音 mp3
│       │   └── bgm/                       # 背景音乐
│       ├── images/                        # 旧版 6 张场景图（baseline）
│       ├── animations/
│       │   ├── hyperframes/               # HTML+GSAP 动画
│       │   │   ├── index.html             # 3幕完整动画 (32s)
│       │   │   ├── scene1.html            # Scene 1 独立 (8s, 用于测试)
│       │   │   └── renders/               # 渲染输出
│       │   └── manim/                     # Manim 科学动画（待写）
│       ├── subtitles/                     # SRT 字幕
│       └── output/
│           ├── ep01_v1_baseline.mp4       # 旧版（静图+配音）
│           └── ep01_v2_*.mp4              # 新版（动画+同步）
│
├── shared/
│   ├── voice_prompts/                     # Kevin 声音克隆样本（待录）
│   ├── brand/                             # 品牌配置（颜色/字体/TTS/视频规格）
│   └── bgm/                               # 共享 BGM 库
│
├── pipeline/
│   ├── math_video_pipeline → ~/Projects/math-video-pipeline   # symlink
│   ├── templates/                         # 集数模板
│   ├── render_video.sh / .py              # 旧版合成脚本
│   ├── generate_scenes.py
│   └── generate_subtitles.py
│
├── VIDEO_PIPELINE_PLAN.md                 # 主规划文档（v2）
├── STRUCTURE.md                           # 本文件
├── PROJECT.md / README.md                 # 项目元信息
└── .venv/                                 # Python 3.9 venv（待升级）
```

## 关键决策

1. **所有 EP01 资产集中到 `episodes/ep01/`**，便于复制做 EP02
2. **HyperFrames 不再是独立项目**，合并进 `animations/hyperframes/`
3. **math-video-pipeline 作为外部依赖** via symlink，复用成熟流水线
4. **品牌配置统一到 `shared/brand/`**，所有集数共享
5. **声音样本路径标准化**：`shared/voice_prompts/kevin_prompt.wav`
