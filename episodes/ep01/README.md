# EP01 — Micro LED 是什么？

> 完整工作流构建说明
> 任何人/未来的你都能 `make ep01` 重建这个视频

## 资产

```
ep01/
├── script.md              # 文案（220 字 / 6 段）
├── storyboard.md          # 分镜
├── audio_schedule.json    # 配音时序表（关键！）
├── audio/
│   ├── voiceover/         # ep01_s01.mp3 .. ep01_s06.mp3
│   └── bgm/               # 背景音乐（可选）
├── animations/
│   └── hyperframes/
│       ├── index.html     # GSAP 主时间线（58s）
│       └── renders/       # 渲染中间产物
├── subtitles/             # SRT 字幕
└── output/
    ├── ep01_v1_baseline.mp4  # 旧版静图+配音 baseline
    ├── ep01_v3_full.mp4      # 当前最新版（动画+对齐配音）
    └── ep01_full.mp4         # build_episode.sh 默认输出
```

## 构建

```bash
cd ~/Projects/techscript-video-pipeline

# 一键完整构建
make ep01

# 只渲染动画
make ep01-render

# 只重新合成配音（视频已渲）
make ep01-mix

# 渲染前预览关键帧
make preview EP=ep01 T=2,7,15,18,26,38,50,55
# 看 preview/ep01/p_t*.jpg
```

## 修改文案/配音

1. 改 `script.md`
2. 用 CosyVoice 重新生成 mp3 → 替换 `audio/voiceover/`
3. 调整 `audio_schedule.json` 中的 `start_ms`
4. 如改了时长，同步改 `animations/hyperframes/index.html`：
   - `data-duration` 属性
   - GSAP timeline 中各 scene 的时间点
5. `make ep01-mix`（不需要重渲动画）

## 修改动画

1. 改 `animations/hyperframes/index.html`
2. `make preview EP=ep01 T=...` 看关键帧
3. 满意后 `make ep01`

## 已知约束 / 教训（避免重蹈覆辙）

### 渲染瓶颈（Mac mini 16GB）
- ❌ 不要用 `npx hyperframes render`（多 worker OOM）
- ✅ 用 CDP 自研渲染脚本（单 Chrome + JPEG quality 95）
- ✅ 分批渲染 + 断点续传（每批 100-250 帧）
- ✅ 每个 Runtime.evaluate 加 3s timeout（GSAP 有时会 hang）
- ✅ 每个 captureScreenshot 加 5s timeout

### GSAP 陷阱
- `paused: true` 的 timeline，初始 `tl.set(..., 0)` 不会立即生效
  - 解决：**在 timeline 外用 `gsap.set(...)` 设一遍**，再在 timeline 内重设
  - 另：在 HTML 元素上加 inline `visibility:hidden;opacity:0;` 兜底
- `tl.seek(t)` 在动画正在跑时调用会偶发 hang
  - 解决：用 `tl.pause(); tl.time(t); tl.pause();` 三连
- 字体加载未完成时 seek，文字会跳变
  - 解决：渲染前等 1500ms 让 Noto Sans SC 加载

### 视频参数
- 1920×1080 @ 24fps，H.264 + AAC 192kbps 立体声
- CRF 18，preset medium，faststart（适合网络播放）

## 复用流程做 EP02

```bash
cp -r episodes/ep01 episodes/ep02
# 改 ep02/animations/hyperframes/index.html 里 composition id
# 改 ep02/script.md + 重生成 voiceover
# 改 ep02/audio_schedule.json
make ep02
```
