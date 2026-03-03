"""
tennis_ball.py —— 在生日启动画面中物理弹跳的网球
带旋转的白色弧形接缝纹路与地面软阴影。
"""
from __future__ import annotations
import math
import random
import pygame


class BouncingTennisBall:
    """物理弹跳网球：重力 + 弹性碰壁 + 旋转接缝动画。"""

    C_BALL  = (188, 238,  26)   # 荧光黄绿
    C_SHADE = (138, 185,  16)   # 深色描边
    C_SEAM  = (255, 255, 255)   # 接缝白
    C_GLOW  = (218, 255,  80)   # 高光

    def __init__(
        self,
        sw: int,
        sh: int,
        r: int = 16,
        y_min: int = 0,
    ) -> None:
        self.r  = r
        self.sw = sw
        self.sh = sh

        self.x   = float(random.randint(r + 20, sw - r - 20))
        self.y   = float(random.randint(max(r, y_min), sh - r - 20))
        spd      = random.uniform(3.0, 5.5)
        ang      = random.uniform(0, 2 * math.pi)
        self.vx  = spd * math.cos(ang)
        self.vy  = spd * math.sin(ang)
        self.rot     = float(random.randint(0, 360))
        self.rot_spd = random.uniform(-8.0, 8.0)

    def update(self) -> None:
        self.x  += self.vx
        self.y  += self.vy
        self.rot = (self.rot + self.rot_spd) % 360

        # 碰壁反弹
        if self.x - self.r <= 0:
            self.x  = float(self.r)
            self.vx = abs(self.vx)
        elif self.x + self.r >= self.sw:
            self.x  = float(self.sw - self.r)
            self.vx = -abs(self.vx)
        if self.y - self.r <= 0:
            self.y  = float(self.r)
            self.vy = abs(self.vy)
        elif self.y + self.r >= self.sh:
            self.y  = float(self.sh - self.r)
            self.vy = -abs(self.vy)

    def draw(self, surface: pygame.Surface) -> None:
        ix, iy = int(self.x), int(self.y)
        r = self.r

        # ── 地面阴影（扁椭圆） ────────────────────────────────────
        shad_w, shad_h = r * 2 + 8, r // 2 + 4
        shad = pygame.Surface((shad_w, shad_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 100, 0, 55),
                            (0, 0, shad_w, shad_h))
        surface.blit(shad, (ix - r - 4, iy + r - 2))

        # ── 球体 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_BALL, (ix, iy), r)

        # ── 旋转接缝（两组对称 S 形曲线） ────────────────────────
        rad = math.radians(self.rot)
        for sign in (1, -1):
            pts: list[tuple[int, int]] = []
            for k in range(15):
                t = k / 14
                a  = rad + sign * math.pi * t
                px = ix + int(r * 0.85 * math.cos(a))
                py = iy + int(r * 0.60 * math.sin(a)
                              + sign * r * 0.32 * math.cos(2 * a))
                pts.append((px, py))
            pygame.draw.lines(surface, self.C_SEAM, False, pts, 2)

        # ── 高光 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_GLOW,
                           (ix - r // 3, iy - r // 3), max(2, r // 3))

        # ── 描边 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_SHADE, (ix, iy), r, 2)
