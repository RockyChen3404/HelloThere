"""
food.py —— 食物实体
以旋转网球样式显示（荧光黄绿 + 白色弧形接缝）。
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
import pygame
import settings


class Food:
    """食物以网球图标显示，带旋转缝线动画与脉冲缩放。"""

    C_BALL  = (188, 238,  26)   # 荧光黄绿
    C_SHADE = (138, 185,  16)   # 深色描边
    C_SEAM  = (255, 255, 255)   # 白色接缝
    C_GLOW  = (218, 255,  80)   # 高光

    def __init__(self) -> None:
        self.position: Tuple[int, int] = (0, 0)
        self._tick: int = 0

    # ── 随机生成到空白格 ──────────────────────────────────────────
    def spawn(self, occupied: List[Tuple[int, int]]) -> None:
        all_cells = [
            (x, y)
            for x in range(settings.GRID_COLS)
            for y in range(settings.GRID_ROWS)
        ]
        free = [c for c in all_cells if c not in occupied]
        if free:
            self.position = random.choice(free)

    # ── 逻辑更新（推进动画帧） ────────────────────────────────────
    def update(self) -> None:
        self._tick = (self._tick + 1) % 60

    # ── 绘制网球 ──────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        gx, gy = self.position
        px = gx * settings.CELL_SIZE
        py = gy * settings.CELL_SIZE + settings.HUD_HEIGHT
        cs = settings.CELL_SIZE
        cx = px + cs // 2
        cy = py + cs // 2

        # 脉冲半径（±1px）
        pulse = math.sin(self._tick * math.pi / 30)
        r = max(4, int(cs // 2 - 2 - pulse))

        # ── 球体 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_BALL, (cx, cy), r)

        # ── 旋转接缝（每帧转 4°） ────────────────────────────────
        rot_rad = math.radians(self._tick * 4)
        for sign in (1, -1):
            pts: list[tuple[int, int]] = []
            for k in range(9):
                t  = k / 8
                a  = rot_rad + sign * math.pi * t
                qx = cx + int(r * 0.78 * math.cos(a))
                qy = cy + int(r * 0.55 * math.sin(a)
                              + sign * r * 0.28 * math.cos(2 * a))
                pts.append((qx, qy))
            if len(pts) >= 2:
                pygame.draw.lines(surface, self.C_SEAM, False, pts, 1)

        # ── 高光 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_GLOW,
                           (cx - r // 3, cy - r // 3), max(1, r // 3))

        # ── 描边 ─────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_SHADE, (cx, cy), r, 1)
