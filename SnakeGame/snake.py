from __future__ import annotations
from typing import List, Tuple
import pygame
import settings

Direction = Tuple[int, int]

UP:    Direction = ( 0, -1)
DOWN:  Direction = ( 0,  1)
LEFT:  Direction = (-1,  0)
RIGHT: Direction = ( 1,  0)

OPPOSITE: dict[Direction, Direction] = {
    UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT,
}

KEY_MAP: dict[int, Direction] = {
    pygame.K_UP:    UP,
    pygame.K_w:     UP,
    pygame.K_DOWN:  DOWN,
    pygame.K_s:     DOWN,
    pygame.K_LEFT:  LEFT,
    pygame.K_a:     LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d:     RIGHT,
}


class Snake:
    """贪吃蛇实体，管理身体坐标、移动与碰撞检测。"""

    def __init__(self) -> None:
        # 初始位置：屏幕中央，初始长度 3
        cx = settings.GRID_COLS // 2
        cy = settings.GRID_ROWS // 2
        self.body: List[Tuple[int, int]] = [
            (cx, cy),
            (cx - 1, cy),
            (cx - 2, cy),
        ]
        self.direction: Direction = RIGHT
        self._next_direction: Direction = RIGHT
        self._grew: bool = False

    # ------------------------------------------------------------------
    # 输入处理
    # ------------------------------------------------------------------
    def handle_key(self, key: int) -> None:
        """根据按键更新下一帧方向（禁止反向）。"""
        new_dir = KEY_MAP.get(key)
        if new_dir and new_dir != OPPOSITE[self.direction]:
            self._next_direction = new_dir

    # ------------------------------------------------------------------
    # 移动
    # ------------------------------------------------------------------
    def move(self) -> None:
        """向当前方向前进一格。"""
        self.direction = self._next_direction
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self._grew:
            self._grew = False
        else:
            self.body.pop()

    def grow(self) -> None:
        """标记下一次移动时保留尾部（增长）。"""
        self._grew = True

    # ------------------------------------------------------------------
    # 碰撞检测
    # ------------------------------------------------------------------
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def hit_wall(self) -> bool:
        hx, hy = self.head()
        return not (0 <= hx < settings.GRID_COLS and 0 <= hy < settings.GRID_ROWS)

    def hit_self(self) -> bool:
        return self.head() in self.body[1:]

    def is_dead(self) -> bool:
        return self.hit_wall() or self.hit_self()

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        for i, (gx, gy) in enumerate(self.body):
            x = gx * settings.CELL_SIZE
            y = gy * settings.CELL_SIZE + settings.HUD_HEIGHT
            rect = pygame.Rect(x, y, settings.CELL_SIZE, settings.CELL_SIZE)

            color = settings.SNAKE_HEAD if i == 0 else settings.SNAKE_BODY
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, settings.SNAKE_OUTLINE, rect,
                             width=1, border_radius=4)

            # 蛇头绘制眼睛
            if i == 0:
                self._draw_eyes(surface, x, y)

    def _draw_eyes(self, surface: pygame.Surface, x: int, y: int) -> None:
        cs = settings.CELL_SIZE
        dx, dy = self.direction
        # 眼睛偏移随方向旋转
        if (dx, dy) == (1, 0):   # 右
            eye_positions = [(x + cs - 5, y + 4), (x + cs - 5, y + cs - 6)]
        elif (dx, dy) == (-1, 0): # 左
            eye_positions = [(x + 3, y + 4), (x + 3, y + cs - 6)]
        elif (dx, dy) == (0, -1): # 上
            eye_positions = [(x + 4, y + 3), (x + cs - 6, y + 3)]
        else:                     # 下
            eye_positions = [(x + 4, y + cs - 5), (x + cs - 6, y + cs - 5)]
        for pos in eye_positions:
            pygame.draw.circle(surface, settings.WHITE, pos, 2)
            pygame.draw.circle(surface, settings.BLACK, pos, 1)
