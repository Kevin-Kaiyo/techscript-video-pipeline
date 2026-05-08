# 🔵 Micro LED 科普短视频项目

> **面向大众的 Micro LED 入门科普视频工程**
> 60 秒 | 16:9 1080P | 普通话配音 | 科技简约蓝白风

---

## 项目简介

本项目用于制作系列 Micro LED 大众科普短视频，采用规范化工程结构管理所有资产、脚本、配置与产出物，可直接导入 OpenClaw 复用，也可上传 GitHub 开源归档。

## 核心定位

| 维度 | 说明 |
|------|------|
| 受众 | 普通大众，无需专业背景 |
| 时长 | 60 秒以内（短视频平台标准） |
| 画面 | 16:9 横屏 1080P（1920×1080） |
| 风格 | 科技简约蓝白风，动态信息图 |
| 语言 | 普通话配音 + 同步中文字幕 |
| 音乐 | 轻柔科技风背景音乐 |

## 目录结构

```
microled-science-video/
├── README.md               # 本文件
├── PROJECT.md              # 项目规划与里程碑
├── .openclaw/
│   └── project.json        # OpenClaw 项目配置
├── .github/
│   └── workflows/          # CI/CD（可选）
├── config/
│   ├── video.json          # 视频技术参数
│   ├── brand.json          # 品牌色彩字体配置
│   └── tts.json            # 配音参数
├── scripts/
│   ├── ep01_intro.md       # EP01 完整文案脚本
│   └── template_episode.md # 单集脚本模板
├── templates/
│   ├── scene_template.md   # 场景卡片模板
│   └── storyboard.md       # 分镜模板
├── assets/
│   ├── images/             # 场景图像素材
│   ├── audio/              # 配音 + 背景音乐
│   ├── video/              # 中间视频素材
│   └── fonts/              # 字体文件
├── production/
│   └── scenes/             # 分场景制作文件
└── output/                 # 最终输出视频
```

## 快速开始

### 1. 制作新一集视频

1. 复制 `scripts/template_episode.md` → 填写文案
2. 按 `templates/scene_template.md` 拆分场景
3. 用 OpenClaw 生成各场景图像素材
4. 用 `sag` 工具生成普通话配音
5. 用 `music_generate` 生成背景音乐
6. 用 `remotion-video-toolkit` 合成最终视频

### 2. 导入 OpenClaw

```bash
# 在 OpenClaw workspace 中直接引用
cd ~/.openclaw/workspace
ln -s ~/Projects/microled-science-video projects/microled-science-video
```

### 3. 上传 GitHub

```bash
cd ~/Projects/microled-science-video
git remote add origin https://github.com/Kevin-Kaiyo/microled-science-video.git
git push -u origin main
```

## 系列规划

| 集数 | 主题 | 状态 |
|------|------|------|
| EP01 | Micro LED 是什么？ | ✅ 脚本完成 |
| EP02 | 为什么比 OLED 更好？ | 📝 规划中 |
| EP03 | Micro LED 在哪里用？ | 📝 规划中 |
| EP04 | 未来的显示技术路线图 | 📝 规划中 |

## 版权

© 2026 Kaiyo Nan / Artronex | CC BY-NC 4.0
