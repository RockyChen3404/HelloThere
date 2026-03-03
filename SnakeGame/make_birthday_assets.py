"""
make_birthday_assets.py
────────────────────────
为远远的12岁生日生成装饰版照片 by_birthday.png。

用法:
    python make_birthday_assets.py
    或由 game.py 在启动时自动调用。
"""
from __future__ import annotations
import math
import os
from PIL import (
    Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── 工具：绘制 N 角星 ────────────────────────────────────────────
def _star_pts(cx: float, cy: float, r_out: float, r_in: float,
              n: int = 5) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(n * 2):
        angle = math.radians(-90 + i * 180 / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(angle),
                    cy + r * math.sin(angle)))
    return pts


# ── 工具：绘制圆角矩形渐变边框 ───────────────────────────────────
def _glow_ring(draw: ImageDraw.ImageDraw,
               cx: int, cy: int, r: int,
               color_inner: tuple, color_outer: tuple,
               steps: int = 10) -> None:
    for i in range(steps, 0, -1):
        frac = i / steps
        c = tuple(int(color_inner[k] * frac + color_outer[k] * (1 - frac))
                  for k in range(3))
        alpha = int(255 * (frac ** 0.6))
        expand = steps - i
        draw.ellipse(
            [cx - r - expand, cy - r - expand,
             cx + r + expand, cy + r + expand],
            outline=(*c, alpha), width=2,
        )


# ── 主函数 ───────────────────────────────────────────────────────
def make_birthday_photo(
    input_path: str,
    output_path: str,
    photo_size: int = 190,
) -> None:
    """
    将 input_path 的照片裁圆、增强，
    加金色星环边框，存为 output_path（PNG，带透明通道）。
    """
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # ── 1. 智能裁方（向上偏 10% 以多显示面部） ──────────────────
    side = min(w, h)
    left = (w - side) // 2
    top  = max(0, int((h - side) // 2 - h * 0.10))
    img  = img.crop((left, top, left + side, top + side))
    img  = img.resize((photo_size, photo_size), Image.LANCZOS)

    # ── 2. 细腻增强（亮度 +8%、对比 +12%、饱和 +15%、磨皮） ───
    img = ImageEnhance.Brightness(img).enhance(1.08)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(1.15)
    img = img.filter(ImageFilter.SMOOTH_MORE)

    # ── 3. 圆形遮罩 ───────────────────────────────────────────────
    mask = Image.new("L", (photo_size, photo_size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, photo_size - 1, photo_size - 1],
                                 fill=255)
    img.putalpha(mask)

    # ── 4. 带光晕边框的画布 ───────────────────────────────────────
    pad    = 30          # 圆外留给星/光晕的空间
    total  = photo_size + pad * 2
    canvas = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    cx, cy = total // 2, total // 2
    r = photo_size // 2

    draw = ImageDraw.Draw(canvas)

    # 外层光晕 (多层半透明圆环渐变)
    _glow_ring(draw, cx, cy, r + 2,
               (255, 220, 40), (255, 100, 0), steps=12)

    # 实心金色边框（3px）
    for off, color in [(2, (255, 235, 80, 255)),
                       (1, (255, 200,  0, 255)),
                       (0, (200, 140,  0, 255))]:
        draw.ellipse([cx - r - off, cy - r - off,
                      cx + r + off, cy + r + off],
                     outline=color, width=2)

    # ── 5. 贴照片 ─────────────────────────────────────────────────
    canvas.paste(img, (pad, pad), img)

    # ── 6. 八颗五角星均匀分布在边框外圈 ─────────────────────────
    ring_r  = r + 18
    for i in range(8):
        angle = math.radians(i * 45 - 22.5)
        sx    = cx + ring_r * math.cos(angle)
        sy    = cy + ring_r * math.sin(angle)
        pts   = _star_pts(sx, sy, 8, 3.5, 5)
        draw.polygon(pts, fill=(255, 220, 30, 240))
        draw.polygon(pts, outline=(200, 155, 0, 255), width=1)

    # ── 7. 顶部小皇冠图案（三个金三角） ─────────────────────────
    crown_cx = cx
    crown_y  = pad - 14
    for offset in (-16, 0, 16):
        tip = (crown_cx + offset, crown_y - (10 if offset == 0 else 6))
        left_b  = (crown_cx + offset - 8, crown_y + 4)
        right_b = (crown_cx + offset + 8, crown_y + 4)
        draw.polygon([tip, left_b, right_b],
                     fill=(255, 215, 0, 230))
        draw.polygon([tip, left_b, right_b],
                     outline=(200, 150, 0, 255), width=1)

    # ── 8. 保存 ───────────────────────────────────────────────────
    canvas.save(output_path, "PNG")
    print(f"✓ 已生成生日照片: {output_path}  ({total}×{total}px)")


# ── 独立运行 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    src = os.path.join(BASE_DIR, "by.jpg")
    dst = os.path.join(BASE_DIR, "by_birthday.png")
    if not os.path.exists(src):
        print(f"✗ 找不到照片: {src}")
    else:
        make_birthday_photo(src, dst)
