"""
Pythagorean Theorem — 3Blue1Brown 风格（无 LaTeX 版）
用 Text 替代 MathTex，避免 LaTeX 依赖。装好 BasicTeX 后再切完整版。
"""
from manim import *
import numpy as np

BG_COLOR = "#0E1117"
A_COLOR = BLUE_C       # #58C4DD
B_COLOR = GREEN_C      # #83C167
C_COLOR = YELLOW_D
SQUARE_OPACITY = 0.55

config.background_color = BG_COLOR
config.frame_rate = 60
config.pixel_width = 1920
config.pixel_height = 1080


def Sym(text, color=WHITE, size=44):
    """用 Text 替代 MathTex，使用 unicode 上标 ² ³"""
    return Text(text, font="Helvetica Neue", color=color, font_size=size, weight=BOLD)


class PythagoreanTheorem(Scene):
    def construct(self):
        # ── Scene 1: 标题 ──
        title = Text("勾股定理", font="PingFang SC", font_size=72, weight=BOLD)
        subtitle = Text(
            "PYTHAGOREAN  THEOREM",
            font="Helvetica Neue", font_size=22, color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)
        title_group = VGroup(title, subtitle).move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.3, run_time=1.2))
        self.play(FadeIn(subtitle, run_time=0.8))
        self.wait(1.0)
        self.play(title_group.animate.scale(0.55).to_edge(UP, buff=0.4), run_time=1.0)

        # ── Scene 2: 三角形 ──
        scale = 0.85
        a_len = 3 * scale
        b_len = 4 * scale

        origin = LEFT * 3.5 + DOWN * 1.6
        p_right_angle = origin
        p_right       = origin + RIGHT * a_len
        p_top         = origin + UP * b_len

        triangle = Polygon(
            p_right_angle, p_right, p_top,
            color=WHITE, stroke_width=3, fill_opacity=0,
        )
        self.play(Create(triangle), run_time=2.0)

        right_angle = Square(side_length=0.25, stroke_width=1.5, color=GREY_B) \
            .move_to(p_right_angle + RIGHT * 0.125 + UP * 0.125)
        self.play(Create(right_angle), run_time=0.4)

        # 边长标签
        label_a = Sym("a", color=A_COLOR, size=44).next_to(
            Line(p_right_angle, p_right), DOWN, buff=0.18)
        label_b = Sym("b", color=B_COLOR, size=44).next_to(
            Line(p_right_angle, p_top), LEFT, buff=0.18)
        hyp_mid = (p_right + p_top) / 2
        hyp_dir = normalize(p_top - p_right)
        normal = np.array([-hyp_dir[1], hyp_dir[0], 0])
        label_c = Sym("c", color=C_COLOR, size=48).move_to(hyp_mid + normal * 0.4)

        self.play(Write(label_a), Write(label_b), run_time=0.7)
        self.play(Write(label_c), run_time=0.5)
        self.wait(1.0)

        # ── Scene 3: 公式 ──
        formula = VGroup(
            Sym("a²", color=A_COLOR, size=92),
            Sym(" + ", color=WHITE, size=92),
            Sym("b²", color=B_COLOR, size=92),
            Sym(" = ", color=WHITE, size=92),
            Sym("c²", color=C_COLOR, size=92),
        ).arrange(RIGHT, buff=0.1).move_to(RIGHT * 3.2 + UP * 1.2)

        for piece in formula:
            self.play(Write(piece), run_time=0.45)
        self.wait(1.0)

        # ── Scene 4: 三个面积正方形 ──
        sq_a = Square(side_length=a_len, color=A_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .move_to((p_right_angle + p_right) / 2 + DOWN * a_len / 2)
        sq_b = Square(side_length=b_len, color=B_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .move_to((p_right_angle + p_top) / 2 + LEFT * b_len / 2)
        c_len = np.sqrt(a_len**2 + b_len**2)
        sq_c_center = hyp_mid + normal * c_len / 2
        angle = np.arctan2(hyp_dir[1], hyp_dir[0])
        sq_c = Square(side_length=c_len, color=C_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .rotate(angle - PI / 2).move_to(sq_c_center)

        sq_a_label = Sym("a²", color=A_COLOR, size=56).move_to(sq_a.get_center())
        sq_b_label = Sym("b²", color=B_COLOR, size=56).move_to(sq_b.get_center())
        sq_c_label = Sym("c²", color=C_COLOR, size=56).move_to(sq_c.get_center())

        self.play(DrawBorderThenFill(sq_a), FadeIn(sq_a_label, scale=0.8), run_time=1.4)
        self.wait(0.4)
        self.play(DrawBorderThenFill(sq_b), FadeIn(sq_b_label, scale=0.8), run_time=1.4)
        self.wait(0.4)
        self.play(DrawBorderThenFill(sq_c), FadeIn(sq_c_label, scale=0.8), run_time=1.6)
        self.wait(1.5)

        # ── Scene 5: 数值实例 ──
        instance = VGroup(
            Sym("3²", color=A_COLOR, size=72),
            Sym(" + ", color=WHITE, size=72),
            Sym("4²", color=B_COLOR, size=72),
            Sym(" = ", color=WHITE, size=72),
            Sym("5²", color=C_COLOR, size=72),
        ).arrange(RIGHT, buff=0.1).move_to(RIGHT * 3.2 + DOWN * 1.0)

        self.play(FadeIn(instance, shift=UP * 0.2), run_time=1.0)

        result = Sym("9 + 16 = 25", color=WHITE, size=56).next_to(instance, DOWN, buff=0.5)
        self.play(Write(result), run_time=1.2)
        self.wait(1.5)

        # ── Scene 6: 收尾高亮 ──
        highlight = Rectangle(
            width=formula.get_width() + 0.6,
            height=formula.get_height() + 0.4,
            color=C_COLOR, stroke_width=2, fill_opacity=0,
        ).move_to(formula)
        self.play(Create(highlight), run_time=1.0)
        self.wait(2.0)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)
        self.wait(0.5)
