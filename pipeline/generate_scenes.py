#!/usr/bin/env python3
"""
Micro LED EP01 场景图像生成器
生成 6 个 1920x1080 科技蓝白风格场景图
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1920, 1080

# 品牌色
BG_DARK   = (10, 14, 26)
BLUE      = (0, 102, 255)
CYAN      = (0, 212, 255)
WHITE     = (255, 255, 255)
GRAY      = (160, 180, 210)
DIM_BLUE  = (20, 40, 80)
ACCENT    = (100, 180, 255)

# 中文字体 (Hiragino Sans GB)
FONT_PATH_CN = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_PATH_EN = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()

def draw_bg_grid(draw, alpha=30):
    """绘制科技网格背景"""
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(*DIM_BLUE, alpha), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(*DIM_BLUE, alpha), width=1)

def draw_particles(img, count=120, seed=42):
    """随机粒子光点"""
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(count):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        r = rng.uniform(1, 4)
        alpha = rng.randint(60, 200)
        color = rng.choice([BLUE, CYAN, WHITE])
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(*color, alpha))

def draw_centered_text(draw, text, y, font, color=WHITE, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=color)

def glow_circle(img, cx, cy, r, color, alpha_peak=200):
    """绘制发光圆圈"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(5, 0, -1):
        a = int(alpha_peak * (i / 5) ** 2)
        ri = r + (5 - i) * 8
        d.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=(*color, a // 4))
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, alpha_peak))
    img = Image.alpha_composite(img, overlay)
    return img

# ── Scene 1: 开场问题 ──────────────────────────────────────────────────────────
def scene1():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 背景渐变（蓝色光晕中心）
    for r in range(500, 0, -10):
        alpha = int(80 * (1 - r/500))
        draw.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(*BLUE, alpha))

    draw_bg_grid(draw, alpha=25)

    # 像素矩阵（模拟屏幕像素放大）
    for row in range(8):
        for col in range(14):
            px = 320 + col * 90
            py = 200 + row * 90
            seed = row * 14 + col
            intensity = (math.sin(seed * 1.3) + 1) / 2
            r_val = int(30 + intensity * 225)
            g_val = int(30 + intensity * 130)
            b_val = int(60 + intensity * 195)
            alpha = int(100 + intensity * 155)
            draw.rounded_rectangle(
                [px, py, px+70, py+70],
                radius=6,
                fill=(r_val, g_val, b_val, alpha),
                outline=(*CYAN, 60),
                width=1
            )

    draw_particles(img, count=80, seed=1)

    # 文字
    font_big = load_font(FONT_PATH_CN, 80, index=0)
    font_sub = load_font(FONT_PATH_CN, 44, index=0)
    font_en = load_font(FONT_PATH_EN, 28)

    draw2 = ImageDraw.Draw(img, "RGBA")
    # 顶部标签
    draw2.rounded_rectangle([40, 40, 320, 90], radius=8, fill=(*BLUE, 200))
    draw2.text((55, 48), "Micro LED 科普 EP01", font=load_font(FONT_PATH_EN, 26), fill=WHITE)

    draw_centered_text(draw2, "手机屏幕里的光", 680, font_big, WHITE)
    draw_centered_text(draw2, "究竟是怎么来的？", 780, font_big, CYAN)
    draw_centered_text(draw2, "Science of Display · Episode 01", 890, font_en, GRAY)

    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s01_opening.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")

# ── Scene 2: LCD vs OLED 对比 ─────────────────────────────────────────────────
def scene2():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_bg_grid(draw, alpha=20)

    # 左侧 LCD 区域
    draw.rectangle([80, 120, 880, 900], fill=(15, 20, 35, 255), outline=(*GRAY, 100), width=2)
    # 右侧 OLED 区域
    draw.rectangle([1040, 120, 1840, 900], fill=(15, 20, 35, 255), outline=(*BLUE, 150), width=2)

    font_title = load_font(FONT_PATH_CN, 58, index=0)
    font_body  = load_font(FONT_PATH_CN, 36, index=0)
    font_label = load_font(FONT_PATH_EN, 52)
    font_sub   = load_font(FONT_PATH_CN, 30, index=0)

    draw2 = ImageDraw.Draw(img, "RGBA")

    # LCD 标题
    draw2.text((260, 150), "LCD 液晶屏", font=font_title, fill=GRAY)
    draw2.text((230, 230), "背光板照亮液晶层", font=font_body, fill=(180, 190, 210))

    # LCD 结构示意
    layers = [
        ("背光板 Backlight", (255, 200, 50), 420),
        ("偏振片 Polarizer", (100, 150, 200), 510),
        ("液晶层 LCD", (60, 120, 180), 600),
        ("彩色滤光片 CF", (80, 160, 255), 690),
    ]
    for label, color, y in layers:
        draw2.rectangle([150, y, 810, y+70], fill=(*color, 180))
        draw2.text((170, y+18), label, font=font_sub, fill=WHITE)

    draw2.text((240, 800), "❌ 像素不能独立控制", font=font_body, fill=(255, 120, 120))

    # 分隔线
    draw2.line([(960, 100), (960, 950)], fill=(*DIM_BLUE, 200), width=2)
    draw2.text((925, 500), "VS", font=load_font(FONT_PATH_EN, 48), fill=(*GRAY, 180))

    # OLED 标题
    draw2.text((1220, 150), "OLED 有机屏", font=font_title, fill=CYAN)
    draw2.text((1170, 230), "每个像素自己发光", font=font_body, fill=(160, 220, 255))

    # OLED 像素阵列
    for row in range(6):
        for col in range(10):
            px = 1100 + col * 73
            py = 380 + row * 73
            seed2 = row * 10 + col
            on = (seed2 % 3) != 0
            color2 = random.Random(seed2).choice([BLUE, CYAN, (255, 100, 100), (100, 255, 100)])
            alpha2 = 220 if on else 40
            draw2.rounded_rectangle([px, py, px+60, py+60], radius=4,
                                     fill=(*color2, alpha2))

    draw2.text((1180, 820), "✅ 像素独立发光，但有烧屏风险", font=font_body, fill=(100, 255, 150))

    draw_particles(img, count=60, seed=2)
    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s02_comparison.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")

# ── Scene 3: Micro LED 登场 ───────────────────────────────────────────────────
def scene3():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 辐射状光线
    cx, cy = W//2, H//2
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        x2 = cx + int(900 * math.cos(rad))
        y2 = cy + int(900 * math.sin(rad))
        alpha = random.Random(angle).randint(15, 50)
        draw.line([(cx, cy), (x2, y2)], fill=(*BLUE, alpha), width=1)

    # 大光晕
    for r in range(400, 0, -5):
        alpha = int(60 * (1 - r/400) ** 1.5)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*BLUE, alpha))
    for r in range(200, 0, -4):
        alpha = int(100 * (1 - r/200) ** 1.5)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*CYAN, alpha))

    draw_particles(img, count=200, seed=3)
    draw_bg_grid(draw, alpha=15)

    font_mega = load_font(FONT_PATH_EN, 110)
    font_big  = load_font(FONT_PATH_CN, 72, index=0)
    font_sub  = load_font(FONT_PATH_CN, 40, index=0)
    font_tag  = load_font(FONT_PATH_EN, 32)

    draw2 = ImageDraw.Draw(img, "RGBA")

    # 主标题
    draw_centered_text(draw2, "Micro LED", 280, font_mega, WHITE)
    # 蓝色装饰线
    lw = 600
    draw2.line([(cx-lw//2, 420), (cx+lw//2, 420)], fill=(*CYAN, 200), width=3)
    draw2.line([(cx-lw//2, 428), (cx+lw//2, 428)], fill=(*BLUE, 100), width=1)

    draw_centered_text(draw2, "显示技术的下一代答案", 470, font_big, CYAN)
    draw_centered_text(draw2, "The Next Generation of Display Technology", 580, font_tag, GRAY)

    # 三个特点标签
    tags = ["💡 自发光", "⚡ 超高亮", "♾️ 超长寿命"]
    for i, tag in enumerate(tags):
        tx = 480 + i * 330
        draw2.rounded_rectangle([tx, 700, tx+260, 760], radius=20, fill=(*BLUE, 180))
        tw_bbox = draw2.textbbox((0,0), tag, font=font_sub)
        tw = tw_bbox[2] - tw_bbox[0]
        draw2.text((tx + (260-tw)//2, 710), tag, font=font_sub, fill=WHITE)

    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s03_reveal.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")

# ── Scene 4: 原理解释 - 像素矩阵 ─────────────────────────────────────────────
def scene4():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_bg_grid(draw, alpha=15)

    font_title = load_font(FONT_PATH_CN, 64, index=0)
    font_body  = load_font(FONT_PATH_CN, 38, index=0)
    font_label = load_font(FONT_PATH_EN, 28)
    font_num   = load_font(FONT_PATH_EN, 60)

    # 左侧：放大的 LED 像素阵列
    cols, rows = 12, 8
    cell = 70
    ox, oy = 120, 180

    rng = random.Random(42)
    draw2 = ImageDraw.Draw(img, "RGBA")
    for row in range(rows):
        for col in range(cols):
            px = ox + col * cell
            py = oy + row * cell
            intensity = (math.sin(col * 0.7 + row * 0.5) + 1) / 2
            alpha = int(80 + intensity * 175)
            color = (
                int(20 + intensity * 50),
                int(80 + intensity * 130),
                int(200 + intensity * 55),
            )
            # LED 颗粒
            draw2.ellipse([px+5, py+5, px+cell-8, py+cell-8], fill=(*color, alpha))
            # 发光晕
            if intensity > 0.6:
                for gr in range(3):
                    ga = int(30 * (1 - gr/3))
                    gcx = px + cell//2
                    gcy = py + cell//2
                    gr2 = cell//2 + gr*6
                    draw2.ellipse([gcx-gr2, gcy-gr2, gcx+gr2, gcy+gr2],
                                  fill=(*CYAN, ga))

    # 放大镜框
    draw2.rectangle([ox-5, oy-5, ox+cols*cell+5, oy+rows*cell+5],
                    outline=(*CYAN, 200), width=3)
    draw2.text((ox, oy+rows*cell+15), "← 实际比头发丝细 10 倍 →", font=font_label, fill=(*GRAY, 180))

    # 右侧说明文字
    rx = 950
    draw2.text((rx, 160), "每个像素 =", font=font_title, fill=WHITE)
    draw2.text((rx, 250), "一颗微型 LED", font=font_title, fill=CYAN)

    # 数据卡片
    stats = [
        ("尺寸", "< 100 μm", "比头发丝细 10 倍"),
        ("数量", "百万颗", "单块屏幕"),
        ("控制", "独立驱动", "每颗单独亮灭"),
    ]
    for i, (label, val, desc) in enumerate(stats):
        sy = 380 + i * 200
        draw2.rounded_rectangle([rx, sy, rx+900, sy+160], radius=12, fill=(20, 35, 65, 220))
        draw2.rounded_rectangle([rx, sy, rx+10, sy+160], radius=4, fill=(*BLUE, 255))
        draw2.text((rx+30, sy+15), label, font=font_label, fill=(*GRAY, 200))
        draw2.text((rx+30, sy+50), val, font=font_num, fill=WHITE)
        draw2.text((rx+30, sy+120), desc, font=font_body, fill=CYAN)

    draw_particles(img, count=50, seed=4)
    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s04_principle.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")

# ── Scene 5: 核心优势数据 ─────────────────────────────────────────────────────
def scene5():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_bg_grid(draw, alpha=18)

    font_title = load_font(FONT_PATH_CN, 68, index=0)
    font_num   = load_font(FONT_PATH_EN, 90)
    font_unit  = load_font(FONT_PATH_EN, 40)
    font_label = load_font(FONT_PATH_CN, 42, index=0)
    font_sub   = load_font(FONT_PATH_CN, 30, index=0)

    draw2 = ImageDraw.Draw(img, "RGBA")

    # 标题
    draw_centered_text(draw2, "Micro LED 核心优势", 60, font_title, WHITE)

    # 三栏数据卡片
    cards = [
        {
            "icon": "☀️",
            "value": "10×",
            "label": "亮度超 OLED",
            "desc": "阳光下清晰可见",
            "color": CYAN,
        },
        {
            "icon": "⏱️",
            "value": "100K",
            "label": "寿命超十万小时",
            "desc": "近乎永不老化",
            "color": (100, 255, 180),
        },
        {
            "icon": "✅",
            "value": "0%",
            "label": "烧屏风险",
            "desc": "无残影、无老化",
            "color": (100, 200, 255),
        },
    ]

    card_w = 520
    card_h = 680
    total_w = 3 * card_w + 2 * 40
    start_x = (W - total_w) // 2

    for i, card in enumerate(cards):
        cx = start_x + i * (card_w + 40)
        cy = 200

        # 卡片背景
        draw2.rounded_rectangle(
            [cx, cy, cx+card_w, cy+card_h],
            radius=20,
            fill=(15, 28, 55, 230),
            outline=(*card["color"], 150),
            width=2
        )
        # 顶部色条
        draw2.rounded_rectangle([cx, cy, cx+card_w, cy+8], radius=4, fill=(*card["color"], 255))

        # Icon
        font_icon = load_font(FONT_PATH_CN, 80, index=0)
        draw2.text((cx + card_w//2 - 40, cy + 40), card["icon"], font=font_icon, fill=card["color"])

        # 数值
        val_bbox = draw2.textbbox((0,0), card["value"], font=font_num)
        val_w = val_bbox[2] - val_bbox[0]
        draw2.text((cx + (card_w - val_w)//2, cy + 180), card["value"], font=font_num, fill=WHITE)

        # 标签
        lbl_bbox = draw2.textbbox((0,0), card["label"], font=font_label)
        lbl_w = lbl_bbox[2] - lbl_bbox[0]
        draw2.text((cx + (card_w - lbl_w)//2, cy + 320), card["label"], font=font_label, fill=card["color"])

        # 分割线
        draw2.line([(cx+40, cy+400), (cx+card_w-40, cy+400)], fill=(*card["color"], 80), width=1)

        # 描述
        desc_bbox = draw2.textbbox((0,0), card["desc"], font=font_sub)
        desc_w = desc_bbox[2] - desc_bbox[0]
        draw2.text((cx + (card_w-desc_w)//2, cy + 430), card["desc"], font=font_sub, fill=(*GRAY, 200))

    draw_particles(img, count=80, seed=5)
    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s05_advantages.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")

# ── Scene 6: 应用场景 + 落版 ─────────────────────────────────────────────────
def scene6():
    img = Image.new("RGBA", (W, H), (*BG_DARK, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_bg_grid(draw, alpha=15)

    font_title = load_font(FONT_PATH_CN, 72, index=0)
    font_body  = load_font(FONT_PATH_CN, 40, index=0)
    font_en    = load_font(FONT_PATH_EN, 30)
    font_tag   = load_font(FONT_PATH_CN, 34, index=0)

    draw2 = ImageDraw.Draw(img, "RGBA")

    # 背景光晕
    for r in range(600, 0, -8):
        alpha = int(35 * (1 - r/600))
        draw2.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=(*BLUE, alpha))

    # 标题
    draw_centered_text(draw2, "Micro LED 的未来应用", 50, font_title, WHITE)

    # 4 个应用场景卡片
    scenes = [
        ("⌚", "智能手表", "超薄、超省电"),
        ("🥽", "AR 眼镜", "轻薄透明显示"),
        ("🚗", "汽车大灯", "精准 ADB 光束"),
        ("🖥️", "超大拼接屏", "无缝 8K 显示"),
    ]

    card_w = 400
    card_h = 420
    total_w = 4 * card_w + 3 * 30
    sx = (W - total_w) // 2

    for i, (icon, name, desc) in enumerate(scenes):
        cx = sx + i * (card_w + 30)
        cy = 200

        draw2.rounded_rectangle(
            [cx, cy, cx+card_w, cy+card_h],
            radius=16,
            fill=(18, 30, 60, 220),
            outline=(*BLUE, 120),
            width=2
        )

        # Icon
        font_icon2 = load_font(FONT_PATH_CN, 80, index=0)
        draw2.text((cx + card_w//2 - 40, cy + 30), icon, font=font_icon2)

        # 名称
        nb = draw2.textbbox((0,0), name, font=font_body)
        nw = nb[2] - nb[0]
        draw2.text((cx + (card_w-nw)//2, cy+160), name, font=font_body, fill=CYAN)

        # 描述
        db = draw2.textbbox((0,0), desc, font=font_tag)
        dw = db[2] - db[0]
        draw2.text((cx + (card_w-dw)//2, cy+230), desc, font=font_tag, fill=(*GRAY, 200))

        # 底部光条
        draw2.rounded_rectangle([cx+40, cy+card_h-30, cx+card_w-40, cy+card_h-20],
                                  radius=4, fill=(*CYAN, 150))

    # 落版品牌字
    draw2.line([(W//2-400, 760), (W//2+400, 760)], fill=(*CYAN, 100), width=1)
    draw_centered_text(draw2, "小小的像素  大大的未来", 790, font_title, WHITE)
    draw_centered_text(draw2, "Micro LED · 改变世界的显示技术", 900, font_en, GRAY)

    # 品牌水印
    draw2.text((W-360, H-50), "Kaiyo Nan | Artronex 2026", font=font_en, fill=(*GRAY, 120))

    draw_particles(img, count=100, seed=6)
    img = img.convert("RGB")
    path = os.path.join(OUTPUT_DIR, "ep01_s06_applications.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"✅ {path}")


if __name__ == "__main__":
    print("🎨 生成 Micro LED EP01 场景图像...")
    scene1()
    scene2()
    scene3()
    scene4()
    scene5()
    scene6()
    print("\n🎉 全部场景图像生成完毕！")
    print(f"📁 输出目录：{OUTPUT_DIR}")
