#!/usr/bin/env bash
# pipeline/manim/README.md
# Manim 渲染说明
cat << 'EOF'
# Manim 渲染引擎

用于技术/算法类视频，类似 3Blue1Brown 风格的数学几何动画。

## 安装

```bash
pip install manim
# macOS 还需要
brew install cairo ffmpeg
```

注意：Manim 需要安装在 cosyvoice_local 的 venv 或系统 Python 里，不要装在 .venv-tts 里。

## 运行示例（勾股定理）

```bash
cd ~/Projects/techscript-video-pipeline/pipeline/manim

# 渲染（无 LaTeX 依赖，推荐）
manim pythagoras_nolatex.py PythagoreanTheoremNoLatex -qh --fps 24

# 输出在 media/videos/pythagoras_nolatex/1080p24/
```

## 适用场景

- 数学公式推导
- 几何原理可视化
- 算法步骤演示（如巨量转移工艺流程）
- 物理/光学原理

## 与 HyperFrames 的区别

| 维度 | Manim | HyperFrames |
|------|-------|-------------|
| 适合内容 | 数学/算法/几何 | 产业链/数据/流程图 |
| 风格 | 3B1B 学术风 | 科技信息图风 |
| 开发语言 | Python | HTML+GSAP+JS |
| 渲染方式 | 本地 Python | Chrome CDP |
| 灵活性 | 几何动画极强 | 布局/数据展示极强 |
EOF
