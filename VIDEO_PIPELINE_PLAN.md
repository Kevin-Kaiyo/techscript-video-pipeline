# 🎬 TechScript Video Pipeline — 完整规划文档

> 目标：把复杂半导体技术，用视频变成任何人都能看懂的内容
> 作者：Kevin (Kaiyo Nan) + AI 龙虾宝宝 🦞
> 创建：2026-05-17 | 最后更新：2026-05-17（Opus 深度复审）

---

## 一、现有资产清单

### 已跑通的工具链

| 工具 | 项目路径 | 状态 | 能力 |
|---|---|---|---|
| HyperFrames 0.6.15 | `microled-hyperframes-demo` | ✅ 已安装 | HTML+GSAP→视频，AI原生 |
| CosyVoice 300M-SFT | `cosyvoice_local` | ✅ 已部署 | 本地中文TTS，无需API |
| Fun-CosyVoice3-0.5B | `cosyvoice_local` | ✅ 已部署 | 更强v3，待验证时间戳输出 |
| Remotion | `math-explainer` | ✅ 已验证 | React 帧精准动画 |
| ElevenLabs (sag) | OpenClaw skill | ✅ 可用 | 高质量多语种TTS（备用） |
| FFmpeg 8.1 | 系统 | ✅ 已安装 | 视频合成/转码 |
| Manim CE | `math-video-pipeline` | ❌ 未安装 | 需重装：`pip install manim` |
| Puppeteer | npx cache | ✅ 可调用 | 备用渲染：逐帧截图 |

### 已有内容成品

| 成品 | 路径 | 时长 | 质量评估 |
|---|---|---|---|
| EP01 MicroLED简介（旧版）| `techscript-video-pipeline/output/ep01_microled_intro.mp4` | 57s | ⚠️ 静图+配音，音画同步差 |
| EP01 HyperFrames动画（新）| `microled-hyperframes-demo/index.html` | 32s | ✅ 3幕动画，视觉效果优秀 |
| 勾股定理 Manim | `math-video-pipeline/outputs/pythagoras_manim_latex_cosyvoice_v1.mp4` | — | ✅ LaTeX质量好 |

### HyperFrames EP01 动画关键帧（已验证）

AI 视觉评估结论：
- ✅ 整体视觉质量强，科技感准确，色彩逻辑清晰（黄=LCD/耗电，紫=OLED/烧屏，青=MicroLED/未来）
- ✅ 中文渲染正确，无乱码
- ⚠️ Scene 1 开场偏空，需加像素矩阵或扫描线元素
- ⚠️ 中文副标题改为「小小像素，大大未来」更自然

---

## 二、问题诊断（按严重程度）

### P0 — 硬件渲染瓶颈
HyperFrames 使用 Chrome headless，每个进程需要 ~256MB RAM。Mac mini 16GB RAM 但几乎占满（WindowServer 1.5GB + CloudflareWARP 1.4GB + 其他），导致渲染中途 OOM killed。

**解决方案（已确定）：** 用 **Puppeteer 逐帧截图 + FFmpeg 合成**替代 HyperFrames 内置渲染器，彻底绕过多进程内存问题。

### P1 — Manim 未安装
`manim not found`，EP03/EP05（工艺流程/工程分析）依赖 Manim，需重装。

### P2 — 音画同步方案未验证
规划中的"CosyVoice 时间戳驱动 Manim 时间轴"方案尚未实验验证：
- CosyVoice 300M-SFT 是否支持字级时间戳输出？
- Fun-CosyVoice3-0.5B 的接口差异？
- Kevin 声音克隆所需数据和步骤？

### P3 — 流水线碎片化
多个工具链孤立运行，每次制作都需要手工串联。

### P4 — 内容规划薄
EP02-EP05 只有标题，没有脚本和分镜。内容生产线是视频工厂的核心。

---

## 三、整体架构设计（v2）

```
┌─────────────────────────────────────────────────────────┐
│                   CONTENT LAYER（内容层）                 │
│  OpenClaw AI → 中文脚本生成 → 分镜/时间轴 → 场景卡片      │
└───────────────────────┬─────────────────────────────────┘
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  科学动画层  │  │  信息图层   │  │   配音层    │
│   Manim     │  │ HyperFrames │  │ CosyVoice   │
│ (公式/结构/ │  │ (标题/对比/ │  │ (本地TTS /  │
│  工艺流程)  │  │  数据可视化)│  │  声音克隆)  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       └────────────────┼─────────────────┘
                        │
                        ↓ 备用渲染路径（P0修复）
               Puppeteer 逐帧 + FFmpeg
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  COMPOSE LAYER（合成层）                  │
│  FFmpeg → 时间戳对齐 → 字幕烧录 → BGM混音 → MP4输出       │
└─────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                PUBLISH LAYER（分发层）                    │
│  博客（Astro）→ LinkedIn → YouTube / Bilibili → Twitter  │
└─────────────────────────────────────────────────────────┘
```

### 工具分工（v2）

| 场景类型 | 工具 | 理由 |
|---|---|---|
| 标题/信息图/对比/数据可视化 | HyperFrames | HTML+GSAP，AI直接生成，设计感强 |
| 数学公式/原理图/工艺流程 | Manim | LaTeX原生，科学精度无可替代 |
| 中文配音（标准速出）| CosyVoice 300M-SFT | 本地，无API依赖 |
| 中文配音（高质量/Kevin声音）| Fun-CosyVoice3-0.5B | 声音克隆 |
| 配音（紧急/高质量备用）| ElevenLabs (sag) | 质量最佳，有网络依赖 |
| 渲染输出 | Puppeteer + FFmpeg | 绕过内存瓶颈 |
| 最终合成 | FFmpeg | 音视频对齐，字幕，BGM混音 |

---

## 四、执行路线图（v2）

### Phase 0: 修复阻断器【当前优先级】

- [x] HyperFrames 安装 ✅
- [x] EP01 三幕动画 HTML 完成 ✅
- [x] 7帧关键截图视觉验证 ✅
- [ ] **P0: 实现 Puppeteer+FFmpeg 备用渲染路径，出 Scene 1 的 MP4**
- [ ] **P1: 安装 Manim CE**（`pip install manim`，在 venv 中）
- [ ] 修复 Scene 1 设计（开场加元素，中文副标题修正）

### Phase 1: 第一个完整片段【里程碑：有声音的视频】

- [ ] 用备用渲染路径出 Scene 1 的 8秒 MP4（无声）
- [ ] 复用现有 `ep01_s01.mp3` 配音，FFmpeg 合成第一个有声片段
- [ ] 评估音画节奏感，记录问题
- [ ] **里程碑：一个真正可以播放的 HyperFrames 动画片段**

### Phase 2: 音画同步验证【里程碑：解决核心痛点】

- [ ] 验证 CosyVoice 300M-SFT 时间戳输出能力
- [ ] 验证 Fun-CosyVoice3-0.5B 接口
- [ ] 实现"语音节奏 → 动画时间轴"的驱动脚本
- [ ] A/B 对比：旧版（静图+配音）vs 新版（动画+同步配音）
- [ ] **里程碑：音画同步感明显改善的 30s 对比片段**

### Phase 3: EP01 完整版【里程碑：可发布的成品】

- [ ] 完成全部 6 个场景的 HyperFrames 动画（32s → 57s 完整版）
- [ ] 用 Fun-CosyVoice3-0.5B 重新生成高质量配音
- [ ] Manim 制作 EP03 预备动画（像素矩阵原理）
- [ ] FFmpeg 最终合成，烧录字幕，混入 BGM
- [ ] **里程碑：EP01 v2 正式版，发布博客 + LinkedIn**

### Phase 4: 内容扩展【里程碑：系列化生产】

- [ ] EP02 脚本（MicroLED vs OLED vs LCD，最容易做）
- [ ] Kevin 声音克隆（录制训练数据）
- [ ] 建立 `pipeline.py`：脚本输入 → 视频自动输出
- [ ] GitHub Actions 自动部署

---

## 五、视频系列规划

| 集数 | 标题 | 目标时长 | 动画类型 | 脚本状态 | 优先级 |
|---|---|---|---|---|---|
| EP01 | Micro LED 是什么？ | 57s | HyperFrames（信息图） | ✅ 已有 | 🔴 最高 |
| EP02 | MicroLED vs OLED vs LCD 全面对比 | 60s | HyperFrames（数据对比） | 🔲 待写 | 🟠 高 |
| EP03 | 怎么造 MicroLED？巨量转移揭秘 | 90s | Manim（工艺流程）+ HF | 🔲 待写 | 🟡 中 |
| EP04 | 为什么 MicroLED 还没普及？成本之战 | 60s | HyperFrames（数据图表） | 🔲 待写 | 🟡 中 |
| EP05 | MicroLED 汽车大灯：晶合光电深度分析 | 90s | Manim+HF（工程分析） | 📄 有研究资料 | 🟢 低 |

---

## 六、渲染技术方案对比

| 方案 | RAM需求 | 速度 | 可靠性 | 推荐场景 |
|---|---|---|---|---|
| HyperFrames 原生（多worker）| 高（256MB×N）| 快 | ❌ Mac mini OOM | 内存充足时 |
| HyperFrames `--workers 1` | 中（~400MB）| 慢 | ❌ 仍然OOM | 临时释放内存后 |
| HyperFrames `--docker` | 独立容器 | 中 | ✅ 隔离 | 有 Docker 环境时 |
| **Puppeteer逐帧 + FFmpeg** | 低（单页面）| 慢但可控 | ✅ **当前推荐** | Mac mini 8/16GB |
| 截图关键帧 + FFmpeg插帧 | 极低 | 快 | ⚠️ 质量降低 | 快速预览 |

---

## 七、分发策略（新增）

| 平台 | 格式 | 规格 | 字幕 |
|---|---|---|---|
| 个人博客（kaiyo-blog） | 横版 MP4 | 1920×1080, H.264 | 硬字幕 |
| LinkedIn | 横版 MP4 | 1920×1080, ≤10min | 硬字幕 |
| YouTube | 横版 MP4 | 1920×1080 | SRT上传 |
| Bilibili（未来）| 横版 MP4 | 1920×1080 | 硬字幕 |
| Twitter/X | 横版 MP4 | ≤2:20 精华版 | 硬字幕 |

---

## 八、当前立即执行清单

```
【P0 阻断器修复 — 今日目标】

Step 1 → 实现 Puppeteer+FFmpeg 备用渲染，出 Scene 1 的 8s MP4
Step 2 → 修复 Scene 1 设计（开场空旷问题 + 中文文案）
Step 3 → 复用现有配音，FFmpeg 合成第一个有声视频片段
Step 4 → 安装 Manim CE（venv 中）

【后续里程碑】

Step 5 → 验证 CosyVoice 时间戳输出
Step 6 → 完整 EP01 v2 制作
Step 7 → 发布博客 + LinkedIn
```

---

*文档版本：v2.0（Opus 深度复审）| 由 OpenClaw 龙虾宝宝 🦞 协助生成*
