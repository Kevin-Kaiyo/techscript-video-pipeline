from manim import *
import numpy as np

config.background_color = "#0A0E1A"
config.frame_rate = 30
config.pixel_width = 1920
config.pixel_height = 1080

BLUE = "#0066FF"
CYAN = "#00D4FF"
GREEN = "#35D07F"
YELLOW = "#FFD166"
RED = "#FF5C7A"
PANEL = "#111827"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


def cn(text, size=34, color=TEXT, weight=NORMAL):
    return Text(text, font="PingFang SC", font_size=size, color=color, weight=weight)


def en(text, size=22, color=MUTED, weight=NORMAL):
    return Text(text, font="Helvetica Neue", font_size=size, color=color, weight=weight)


def chip_grid(rows=6, cols=10, cell=0.23, gap=0.06, color=CYAN):
    dots = VGroup()
    for r in range(rows):
        for c in range(cols):
            sq = RoundedRectangle(
                width=cell,
                height=cell,
                corner_radius=0.025,
                stroke_width=1,
                stroke_color=color,
                fill_color=color,
                fill_opacity=0.82,
            )
            sq.move_to(np.array([c * (cell + gap), -r * (cell + gap), 0]))
            dots.add(sq)
    dots.move_to(ORIGIN)
    return dots


def make_panel(label, sublabel, width=4.7, height=3.1):
    box = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.12,
        stroke_width=1.6,
        stroke_color="#28415F",
        fill_color=PANEL,
        fill_opacity=0.78,
    )
    title = cn(label, size=28, weight=BOLD).next_to(box.get_top(), DOWN, buff=0.18)
    subtitle = en(sublabel, size=16).next_to(title, DOWN, buff=0.08)
    return VGroup(box, title, subtitle)


class MicroLEDMassTransfer(Scene):
    def construct(self):
        self.camera.background_color = "#0A0E1A"

        title = cn("Micro LED 巨量转移", size=58, weight=BOLD)
        subtitle = en("Mass Transfer: from wafer to display backplane", size=24)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.18).to_edge(UP, buff=0.32)

        self.play(FadeIn(title, shift=DOWN * 0.25), FadeIn(subtitle), run_time=1.0)

        wafer_panel = make_panel("外延晶圆", "LED wafer").move_to(LEFT * 4.6 + DOWN * 0.2)
        backplane_panel = make_panel("驱动背板", "TFT backplane").move_to(RIGHT * 4.6 + DOWN * 0.2)

        wafer_grid = chip_grid(rows=7, cols=11, color=CYAN).scale(0.92).move_to(wafer_panel[0].get_center() + DOWN * 0.24)
        backplane_grid = chip_grid(rows=7, cols=11, color="#2B3A55").scale(0.92).move_to(backplane_panel[0].get_center() + DOWN * 0.24)
        backplane_grid.set_fill(opacity=0.20).set_stroke(opacity=0.55)

        self.play(FadeIn(wafer_panel), FadeIn(backplane_panel), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in wafer_grid], lag_ratio=0.012), run_time=1.6)
        self.play(FadeIn(backplane_grid), run_time=0.8)

        note = cn("不是搬一颗，而是一次搬几千到几万颗", size=30, color=YELLOW).next_to(title_group, DOWN, buff=0.35)
        self.play(Write(note), run_time=1.0)
        self.wait(0.7)
        self.play(FadeOut(note), run_time=0.5)

        stamp = RoundedRectangle(
            width=3.9,
            height=0.62,
            corner_radius=0.18,
            stroke_width=2.5,
            stroke_color=YELLOW,
            fill_color=YELLOW,
            fill_opacity=0.18,
        )
        stamp_label = cn("弹性转移头", size=24, color=YELLOW, weight=BOLD).move_to(stamp.get_center())
        stamp_group = VGroup(stamp, stamp_label).move_to(wafer_grid.get_top() + UP * 0.7)

        self.play(FadeIn(stamp_group, shift=DOWN * 0.3), run_time=0.8)
        self.play(stamp_group.animate.shift(DOWN * 0.78), run_time=0.9)

        picked = VGroup(*[wafer_grid[i].copy() for i in range(0, len(wafer_grid), 3)])
        for dot in picked:
            dot.set_fill(YELLOW, opacity=0.95).set_stroke(YELLOW, opacity=1)
        self.play(
            LaggedStart(*[Transform(wafer_grid[i], picked[j]) for j, i in enumerate(range(0, len(wafer_grid), 3))], lag_ratio=0.02),
            run_time=1.0,
        )
        self.play(stamp_group.animate.shift(UP * 0.95), picked.animate.shift(UP * 0.95), run_time=0.8)
        self.play(FadeOut(stamp_label), run_time=0.25)
        stamp_group.remove(stamp_label)

        arrow = Arrow(LEFT * 1.45 + UP * 0.7, RIGHT * 1.45 + UP * 0.7, buff=0, color=YELLOW, stroke_width=7)
        arrow_text = cn("对准 · 释放 · 检测", size=30, color=TEXT, weight=BOLD).move_to(DOWN * 3.0)
        self.play(GrowArrow(arrow), FadeIn(arrow_text), run_time=0.9)
        self.play(FadeOut(backplane_panel[1]), FadeOut(backplane_panel[2]), run_time=0.25)
        self.play(stamp_group.animate.move_to(backplane_grid.get_top() + UP * 1.0), picked.animate.move_to(backplane_grid.get_top() + UP * 1.0), run_time=1.4)
        self.play(stamp_group.animate.shift(DOWN * 0.88), picked.animate.shift(DOWN * 0.88), run_time=0.8)

        target_indices = list(range(0, len(backplane_grid), 3))
        placed = VGroup()
        for j, idx in enumerate(target_indices):
            dot = backplane_grid[idx].copy()
            dot.set_fill(GREEN, opacity=0.92).set_stroke(GREEN, opacity=1)
            placed.add(dot)
        self.play(
            LaggedStart(*[Transform(picked[j], placed[j]) for j in range(len(placed))], lag_ratio=0.018),
            run_time=1.1,
        )
        self.play(FadeOut(stamp_group, shift=UP * 0.3), run_time=0.7)

        precision = VGroup(
            cn("核心难点", size=28, color=RED, weight=BOLD),
            cn("微米级对位", size=24),
            cn("高良率释放", size=24),
            cn("坏点检测与修复", size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        precision_box = SurroundingRectangle(precision, color=RED, buff=0.24, corner_radius=0.08)
        precision_group = VGroup(precision_box, precision).move_to(DOWN * 3.0)

        self.play(FadeIn(precision_group, shift=UP * 0.25), run_time=1.0)
        self.wait(0.8)

        rows = VGroup()
        for row in range(7):
            row_group = VGroup()
            for col in range(11):
                idx = row * 11 + col
                dot = backplane_grid[idx].copy()
                dot.set_fill(GREEN if idx % 17 else RED, opacity=0.95)
                dot.set_stroke(GREEN if idx % 17 else RED, opacity=1)
                row_group.add(dot)
            rows.add(row_group)

        self.play(FadeOut(picked), run_time=0.4)
        for row_num, row_group in enumerate(rows):
            start = row_num * 11
            self.play(
                LaggedStart(*[Transform(backplane_grid[start + i], row_group[i]) for i in range(11)], lag_ratio=0.01),
                run_time=0.22,
            )

        bad = cn("坏点必须被识别并修复", size=28, color=RED, weight=BOLD).next_to(backplane_panel[0], DOWN, buff=0.25)
        good = cn("最终形成可驱动像素阵列", size=30, color=GREEN, weight=BOLD).next_to(wafer_panel[0], DOWN, buff=0.25)
        self.play(Write(bad), Write(good), run_time=1.0)
        self.wait(1.0)

        final = VGroup(
            cn("巨量转移 = 精密制造 × 良率工程", size=42, color=TEXT, weight=BOLD),
            en("The bottleneck is not moving pixels. It is moving them accurately, repeatedly, and at yield.", size=20),
        ).arrange(DOWN, buff=0.18).move_to(ORIGIN + DOWN * 0.1)

        self.play(
            FadeOut(wafer_panel),
            FadeOut(backplane_panel),
            FadeOut(wafer_grid),
            FadeOut(backplane_grid),
            FadeOut(precision_group),
            FadeOut(arrow),
            FadeOut(arrow_text),
            FadeOut(bad),
            FadeOut(good),
            run_time=0.9,
        )
        self.play(FadeIn(final, scale=0.94), run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(final), FadeOut(title_group), run_time=0.8)
