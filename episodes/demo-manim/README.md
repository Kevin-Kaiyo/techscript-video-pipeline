# demo-manim — Manim 技术类动画示例

这一集用 Manim 展示「勾股定理」的几何面积证明。

作为 demo-tech 的升级路径：用同样的 Manim 引擎来做 Micro LED 巨量转移原理动画。

## 场景脚本

- `../../pipeline/manim/pythagoras_nolatex.py` — 勾股定理（无 LaTeX，推荐）

## 渲染

```bash
cd ~/Projects/techscript-video-pipeline
manim pipeline/manim/pythagoras_nolatex.py PythagoreanTheoremNoLatex -qh --fps 24
# 输出：media/videos/.../1080p24/PythagoreanTheoremNoLatex.mp4
```

## 状态

- [x] 场景脚本完成
- [ ] 配音脚本 (script.md)
- [ ] 合成最终视频
