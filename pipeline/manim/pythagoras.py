"""
Pythagorean Theorem — 3Blue1Brown 风格
经典面积证明：a² + b² = c²

用 Manim Community Edition 实现
"""
from manim import *
import numpy as np

# 3Blue1Brown 风格配色（已是 Manim 默认，但显式声明更清楚）
BG_COLOR = "#0E1117"   # 比纯黑更高级的深色
A_COLOR = BLUE_C       # #58C4DD
B_COLOR = GREEN_C      # #83C167
C_COLOR = YELLOW_D     # 斜边/结论用黄
SQUARE_OPACITY = 0.55

config.background_color = BG_COLOR
config.frame_rate = 60         # 60fps 丝滑感
config.pixel_width = 1920
config.pixel_height = 1080


class PythagoreanTheorem(Scene):
    def construct(self):
        # ── Scene 1: 标题 ──
        title = Text("勾股定理", font="PingFang SC", font_size=72, weight=BOLD)
        subtitle = Text(
            "PYTHAGOREAN  THEOREM",
            font="Helvetica Neue", font_size=22,
            color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)
        # 字距加宽（Manim 没原生 letter-spacing，用空格 + 弱化色模拟）

        title_group = VGroup(title, subtitle).move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.3, run_time=1.2))
        self.play(FadeIn(subtitle, run_time=0.8))
        self.wait(1.0)
        self.play(
            title_group.animate.scale(0.55).to_edge(UP, buff=0.4),
            run_time=1.0,
        )

        # ── Scene 2: 直角三角形描边生长 ──
        # 直角三角形：a=3, b=4, c=5（缩放到合理尺寸）
        scale = 0.85
        a_len = 3 * scale  # 底（水平）
        b_len = 4 * scale  # 高（垂直）

        # 把三角形放在画面中下偏左
        origin = LEFT * 3.5 + DOWN * 1.6
        p_right_angle = origin
        p_right       = origin + RIGHT * a_len      # 底边右端
        p_top         = origin + UP * b_len         # 高的顶端

        triangle = Polygon(
            p_right_angle, p_right, p_top,
            color=WHITE, stroke_width=3,
            fill_opacity=0,
        )

        # 描边生长（关键：用 Create 而不是 FadeIn）
        self.play(Create(triangle), run_time=2.0)

        # 直角小方块标记
        right_angle = Square(side_length=0.25, stroke_width=1.5, color=GREY_B) \
            .move_to(p_right_angle + RIGHT * 0.125 + UP * 0.125)
        self.play(Create(right_angle), run_time=0.4)

        # 边长标签
        label_a = MathTex("a", color=A_COLOR, font_size=44) \
            .next_to(Line(p_right_angle, p_right), DOWN, buff=0.18)
        label_b = MathTex("b", color=B_COLOR, font_size=44) \
            .next_to(Line(p_right_angle, p_top), LEFT, buff=0.18)
        # 斜边在线段中点偏外
        hyp_mid = (p_right + p_top) / 2
        hyp_dir = normalize(p_top - p_right)
        # 斜边法线方向（向外）
        normal = np.array([-hyp_dir[1], hyp_dir[0], 0])
        label_c = MathTex("c", color=C_COLOR, font_size=48) \
            .move_to(hyp_mid + normal * 0.4)

        self.play(Write(label_a), Write(label_b), run_time=0.7)
        self.play(Write(label_c), run_time=0.5)
        self.wait(1.0)

        # ── Scene 3: 公式从右侧出现 ──
        formula = MathTex(
            "a^2", "+", "b^2", "=", "c^2",
            font_size=92,
        )
        formula[0].set_color(A_COLOR)
        formula[2].set_color(B_COLOR)
        formula[4].set_color(C_COLOR)
        formula.move_to(RIGHT * 3.2 + UP * 1.2)

        self.play(Write(formula), run_time=2.5)
        self.wait(1.0)

        # ── Scene 4: 三个正方形建立在三条边上 ──
        # a² 正方形（在底边下方）
        sq_a = Square(side_length=a_len, color=A_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .move_to((p_right_angle + p_right) / 2 + DOWN * a_len / 2)

        # b² 正方形（在高的左侧）
        sq_b = Square(side_length=b_len, color=B_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .move_to((p_right_angle + p_top) / 2 + LEFT * b_len / 2)

        # c² 正方形（在斜边外侧）
        c_len = np.sqrt(a_len**2 + b_len**2)
        # 中心点 = 斜边中点 + 法线 * c/2
        sq_c_center = hyp_mid + normal * c_len / 2
        # 旋转角度：斜边方向 - 水平方向
        angle = np.arctan2(hyp_dir[1], hyp_dir[0])
        sq_c = Square(side_length=c_len, color=C_COLOR,
                      fill_opacity=SQUARE_OPACITY, stroke_width=2.5) \
            .rotate(angle - PI / 2) \
            .move_to(sq_c_center)

        # a² 标签
        sq_a_label = MathTex("a^2", color=A_COLOR, font_size=56) \
            .move_to(sq_a.get_center())
        sq_b_label = MathTex("b^2", color=B_COLOR, font_size=56) \
            .move_to(sq_b.get_center())
        sq_c_label = MathTex("c^2", color=C_COLOR, font_size=56) \
            .move_to(sq_c.get_center())

        self.play(
            DrawBorderThenFill(sq_a),
            FadeIn(sq_a_label, scale=0.8),
            run_time=1.4,
        )
        self.wait(0.4)
        self.play(
            DrawBorderThenFill(sq_b),
            FadeIn(sq_b_label, scale=0.8),
            run_time=1.4,
        )
        self.wait(0.4)
        self.play(
            DrawBorderThenFill(sq_c),
            FadeIn(sq_c_label, scale=0.8),
            run_time=1.6,
        )
        self.wait(1.5)

        # ── Scene 5: 数值实例 ──
        # 把公式替换为带数字的形式
        instance = MathTex(
            "3^2", "+", "4^2", "=", "5^2",
            font_size=76,
        )
        instance[0].set_color(A_COLOR)
        instance[2].set_color(B_COLOR)
        instance[4].set_color(C_COLOR)
        instance.move_to(RIGHT * 3.2 + DOWN * 1.0)

        self.play(TransformMatchingTex(formula.copy(), instance), run_time=1.5)

        result = MathTex(
            "9", "+", "16", "=", "25",
            font_size=64, color=WHITE,
        ).next_to(instance, DOWN, buff=0.5)
        self.play(Write(result), run_time=1.2)
        self.wait(1.5)

        # ── Scene 6: 收尾 ──
        # 高亮："这就是勾股定理"
        highlight = Rectangle(
            width=formula.get_width() + 0.6,
            height=formula.get_height() + 0.4,
            color=C_COLOR, stroke_width=2,
            fill_opacity=0,
        ).move_to(formula)
        self.play(Create(highlight), run_time=1.0)
        self.wait(2.0)

        # 全部淡出
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=1.2,
        )
        self.wait(0.5)
