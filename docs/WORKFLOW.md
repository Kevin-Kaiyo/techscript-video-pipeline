# 视频生成工作流

## 从零开始制作一集视频

本项目不是 Micro LED 专用工具。Micro LED 只是当前验证素材。新集数可以面向任意半导体科普主题，只要先判断它主要是在讲“信息结构”还是“技术动作”。

### 整体流程

```
1. 写文案    →  script.md
2. 选择渲染器 →  HyperFrames 或 Manim
3. 写动画    →  animations/hyperframes/index.html 或 pipeline/manim/<scene>.py
4. 生成配音  →  tts_cli.py
5. 对齐 schedule →  auto_schedule.mjs
6. 构建前检查 →  preflight.mjs
7. 渲染/合成  →  build_episode.sh 或 build_manim_episode.sh
```

---

## Step 1: 编写文案脚本

在 `episodes/<ep>/script.md` 中，按 `## sNN` 分段：

```markdown
## s01
Micro LED 是下一代显示技术的核心。每颗像素自发光，无需背光板。

## s02
相比 OLED，它亮度提升 10 倍，功耗降低 50%，寿命延长 3 倍。

## s03
2030 年，市场规模预计达到 50 亿美元。这场革命，已经开跑。
```

**建议**：
- 每段 5–12 秒（对应 40–90 字）
- 3–6 段/集，总时长 30–60 秒
- 用短句，避免长定语

---

## Step 2: 制作动画

### 选择渲染工具

```
你的内容是什么类型？
├── 技术动作/物理过程/几何关系/制造机理  →  Manim（见 docs/MANIM.md）
├── 产业链/设备材料/供应链/路线图       →  HyperFrames（继续往下看）
├── 市场数据/对比/节点时间轴             →  HyperFrames
└── 混合型内容                           →  拆成多个 scene，分别渲染后用 FFmpeg 合成
```

### 半导体选题示例

| 主题 | 推荐切法 | 主渲染器 |
|------|----------|----------|
| Hybrid bonding 原理 | 表面平坦化、对准、接触、退火、缺陷 | Manim |
| Hybrid bonding 设备材料 | CMP、清洗、键合机、检测、载片、材料流 | HyperFrames |
| 3D 封装 | chiplet 堆叠、TSV、interposer、热路径 | Manim + HyperFrames |
| CPO / 光互连 | 电互连瓶颈、光引擎位置、供应链角色 | HyperFrames |
| Micro LED 光互连 | 像素阵列、光耦合、微纳结构、系统价值 | Manim + HyperFrames |

原则：**能画成结构图/产业图/数据图的，用 HyperFrames；需要展示运动、接触、变形、对准、扩散、几何推导的，用 Manim。**

### HyperFrames 动画规范

在 `episodes/<ep>/animations/hyperframes/index.html` 中：

**必须有的 HTML 属性**：
```html
<div id="stage"
     data-composition-id="<ep-name>"
     data-start="0"
     data-duration="<秒数>"
     data-width="1920"
     data-height="1080">
```

**必须有的 JS**：
```javascript
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
// ... 你的动画
window.__timelines["<ep-name>"] = tl;
```

**注意事项**：
- ❌ 不要用 `tl.to(el, { className: "active" })` 改 class → 用直接属性动画
- ❌ 不要用 emoji 代替专业图标 → 用 inline SVG
- ✅ 所有箭头用 SVG `<polyline>` / `<line>` 绘制
- ✅ 确保 `data-duration` 与配音总长对齐

---

## Step 3: 生成配音

```bash
# 查看可用 provider 和音色
python pipeline/tts_cli.py --list

# Edge TTS（推荐，免费）
python pipeline/tts_cli.py \
  --provider edge \
  --voice zh-CN-YunjianNeural \
  --ep demo-industry

# 声音克隆（需要 CosyVoice，见 docs/SETUP_COSYVOICE.md）
python pipeline/tts_cli.py \
  --provider cosyvoice-clone \
  --voice voices/kevin/prompt_raw.wav \
  --ep demo-industry
```

生成的文件在：`episodes/<ep>/audio/voiceover/`

---

## Step 4: 自动对齐

```bash
node pipeline/auto_schedule.mjs episodes/<ep>
```

这会：
1. ffprobe 测量每段 mp3 时长
2. 按段顺序拼接，段间 0.3s 间隔
3. 输出 `audio_schedule.json`

⚠️ 如果 schedule 总时长与动画 `data-duration` 差距 > 5s，回去调整脚本长度或动画节奏。

---

## Step 5: 渲染动画帧

先运行 preflight，确认依赖、episode 结构和已生成的 voiceover 文件都存在：

```bash
node pipeline/preflight.mjs <ep>
```

```bash
# 启动 HTTP 服务（新终端）
cd episodes/<ep>/animations/hyperframes
python3 -m http.server 18234

# 回到项目根，分批渲染（推荐每批 300-500 帧）
# FPS 默认来自 shared/brand/video.json；手动调用时需要显式传入。
node pipeline/render_cdp_resumable.mjs \
  30 \                          # FPS
  40 \                          # 总时长(秒)
  /tmp/<ep>_frames \            # 输出帧目录
  <ep-name> \                   # composition id
  "http://localhost:18234/index.html" \
  400                           # 每批帧数

# 如果输出 "N frames remain — run again"，重复运行直到 "All frames complete!"
```

**内存注意**：Mac 8GB 用 batch=300，16GB 可用 batch=500。

---

## Step 6: 合成最终视频

```bash
# 方法 A：一键全流程（包含渲染）
bash pipeline/build_episode.sh <ep>

# 方法 B：只重新合成音轨（不重渲，快）
# 先从已有视频提取静音版
ffmpeg -y -i episodes/<ep>/output/<ep>_full.mp4 -vcodec copy -an /tmp/<ep>_silent.mp4

# 再合成
node pipeline/compose_audio.mjs \
  /tmp/<ep>_silent.mp4 \
  episodes/<ep>/audio/voiceover \
  episodes/<ep>/audio_schedule.json \
  episodes/<ep>/output/<ep>_full.mp4 \
  <总秒数>
```

---

## 常用 Makefile 命令

```bash
make tts EP=demo-tech          # 生成配音
make schedule EP=demo-tech     # 生成 audio_schedule.json
make preflight EP=demo-tech    # 检查构建条件
make preview EP=demo-tech      # 渲染关键帧预览
make build EP=demo-tech        # 完整构建
make manim-build EP=demo-manim # 构建 Manim 技术原理动画
```

创建新 episode：

```bash
npm run scaffold -- <episode-id> <family> [renderer]

# family: principle, process, equipment, industry, data, system
# renderer 可省略；默认按 family 自动选择 Manim / HyperFrames / Mixed
npm run scaffold -- demo-hybrid-bonding-principle principle
npm run scaffold -- demo-hybrid-bonding-supply-chain equipment
```
