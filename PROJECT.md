# PROJECT.md — Micro LED 科普视频项目规划

## 项目信息

| 字段 | 内容 |
|------|------|
| 项目名称 | TechScript Video Pipeline |
| 项目代号 | techscript-video-pipeline |
| 负责人 | Kaiyo Nan |
| 创建日期 | 2026-05-08 |
| 当前版本 | v0.1.0 |
| 目标平台 | B站、抖音、YouTube、LinkedIn |

---

## 制作标准

### 视频规格
- 分辨率：1920×1080（Full HD）
- 帧率：30fps
- 时长：≤60 秒
- 格式：MP4 (H.264)
- 比特率：8-12 Mbps

### 视觉风格
- **主色调**：#0066FF（科技蓝）、#FFFFFF（纯白）、#0A0E1A（深空黑）
- **辅助色**：#00D4FF（青蓝）、#E8F4FD（浅蓝背景）
- **字体**：思源黑体 (CN)、Inter (EN)
- **动效**：简洁过渡、数据动画、粒子光效

### 音频规格
- 配音：普通话标准音，语速 3.5-4 字/秒
- 背景音乐：-20dB 以下，不压主音轨
- 格式：MP3 192kbps 或 WAV 44.1kHz

---

## 里程碑

### Phase 1 — EP01 基础版（当前阶段）

| 任务 | 状态 | 说明 |
|------|------|------|
| 项目工程搭建 | ✅ 完成 | 目录 + 配置 + 模板 |
| EP01 文案脚本 | ✅ 完成 | 6 场景，60 秒 |
| 场景图像生成 | 🔄 制作中 | 用 image_generate |
| 普通话配音 | 🔄 制作中 | 用 sag TTS |
| 背景音乐 | 🔄 制作中 | 用 music_generate |
| 视频合成 | ⏳ 待开始 | 用 remotion 或拼接 |
| EP01 发布 | ⏳ 待开始 | 多平台发布 |

### Phase 2 — EP02-EP04 扩展

待 EP01 完成后规划。

---

## 工作流程 SOP

```
1. 文案脚本 (scripts/)
   ↓
2. 分镜拆解 (production/scenes/)
   ↓
3. 资产生成
   - 图像：image_generate → assets/images/
   - 配音：sag → assets/audio/voiceover/
   - 音乐：music_generate → assets/audio/bgm/
   ↓
4. 视频合成 (remotion-video-toolkit)
   ↓
5. 输出审核 → output/
   ↓
6. 发布归档
```

---

## 变更日志

### v0.1.0 (2026-05-08)
- 初始工程搭建
- EP01 脚本完成
- 项目结构规范化
