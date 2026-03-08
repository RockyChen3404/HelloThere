"""
horse.py —— 马年奔跑骏马逐帧动画
马面向左侧、从屏幕右侧进入、向左奔跑。
"""
from __future__ import annotations
import pygame


class Horse:
    """4 帧周期逐帧动画的奔跑骏马。"""

    # ── 颜色 ──────────────────────────────────────────────────────
    C_BODY   = (210, 148,  58)   # 金棕色
    C_DARK   = (148,  98,  32)   # 深棕（腿/轮廓）
    C_BELLY  = (235, 198, 145)   # 浅腹
    C_MANE   = ( 88,  52,  14)   # 鬃毛/尾巴
    C_HOOF   = ( 52,  36,  20)   # 蹄
    C_EYE    = ( 18,  18,  18)
    C_SHADOW = (  0,   0,   0, 60)  # 地面阴影

    # ── 4 帧腿部配置 ───────────────────────────────────────────────
    # 格式: (根x, 根y, 末x, 末y)  单位 = 逻辑像素（scale=1 时）
    # 左前 / 右前 / 左后 / 右后
    _LEGS: list[list[tuple[int, int, int, int]]] = [
        # 帧0：腾跃展开
        [(22, 46,  8, 68), (30, 48, 22, 70),
         (60, 46, 72, 67), (68, 48, 82, 66)],
        # 帧1：落地收腿
        [(22, 46, 18, 69), (30, 48, 28, 71),
         (60, 46, 62, 69), (68, 48, 70, 71)],
        # 帧2：腾跃展开（前后互换）
        [(22, 46, 30, 68), (30, 48, 40, 69),
         (60, 46, 52, 67), (68, 48, 60, 68)],
        # 帧3：收腿
        [(22, 46, 20, 70), (30, 48, 30, 71),
         (60, 46, 64, 70), (68, 48, 68, 71)],
    ]

    def __init__(
        self,
        screen_w: int,
        y: int,
        scale: float = 1.0,
        speed: float = 3.0,
    ) -> None:
        self.s = scale
        self.screen_w = screen_w
        self.x: float = float(screen_w + int(115 * scale) + 10)
        self.y = y
        self.speed = speed
        self.frame = 0
        self._ft = 0          # 帧计时
        self.active = True
        self._W = int(115 * scale)   # 包围盒宽度

    # ── 逻辑更新 ──────────────────────────────────────────────────
    def update(self) -> None:
        self.x -= self.speed
        self._ft += 1
        if self._ft >= 5:
            self._ft = 0
            self.frame = (self.frame + 1) % 4
        if self.x < -self._W - 10:
            self.active = False

    # ── 绘制 ──────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        # 在临时透明 Surface 上绘制，再 blit 到主面
        w = int(115 * self.s)
        h = int(82 * self.s)
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        self._paint(tmp, 0, 0)
        surface.blit(tmp, (int(self.x), self.y))

    def _paint(self, surf: pygame.Surface, ox: int, oy: int) -> None:
        s = self.s

        def p(x: float, y: float) -> tuple[int, int]:
            return (ox + int(x * s), oy + int(y * s))

        def r(x: float, y: float, w: float, h: float) -> pygame.Rect:
            return pygame.Rect(ox + int(x*s), oy + int(y*s), int(w*s), int(h*s))

        # ── 尾巴（先画，被身体遮） ────────────────────────────────
        tail_pts = [
            [p(88, 28), p(100, 36), p(106, 46)],
            [p(88, 30), p(101, 40), p(105, 52)],
            [p(86, 32), p( 98, 44), p(102, 58)],
        ]
        for pts in tail_pts:
            if len(pts) >= 2:
                pygame.draw.lines(surf, self.C_MANE, False, pts,
                                  max(1, int(3 * s)))

        # ── 腿（被身体遮） ────────────────────────────────────────
        for bx, by, ex, ey in self._LEGS[self.frame]:
            start = p(bx, by)
            end   = p(ex, ey)
            pygame.draw.line(surf, self.C_DARK, start, end,
                             max(2, int(4 * s)))
            # 蹄子
            ex2, ey2 = end
            pygame.draw.ellipse(surf, self.C_HOOF,
                (ex2 - int(3*s), ey2 - int(2*s),
                 int(7*s), int(5*s)))

        # ── 地面阴影（细椭圆） ────────────────────────────────────
        shadow_surf = pygame.Surface((int(80*s), int(10*s)), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 0))
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50),
                            shadow_surf.get_rect())
        surf.blit(shadow_surf, p(10, 72))

        # ── 身体 ─────────────────────────────────────────────────
        pygame.draw.ellipse(surf, self.C_BODY,   r(10, 18, 80, 32))
        pygame.draw.ellipse(surf, self.C_BELLY,  r(22, 28, 46, 18))
        # 臀部（圆润高光）
        pygame.draw.ellipse(surf, self.C_DARK,   r(76, 18, 26, 26))
        pygame.draw.ellipse(surf, self.C_BODY,   r(74, 18, 24, 24))

        # ── 颈部 ─────────────────────────────────────────────────
        neck = [p(26, 18), p(20,  4), p(10, 10), p(18, 26)]
        pygame.draw.polygon(surf, self.C_BODY, neck)

        # ── 头部 ─────────────────────────────────────────────────
        pygame.draw.ellipse(surf, self.C_BODY, r(0, 4, 26, 17))
        # 口鼻
        pygame.draw.ellipse(surf, self.C_DARK, r(0, 12, 10,  9))
        # 鼻孔
        pygame.draw.circle(surf, self.C_MANE, p(3, 15), max(1, int(2*s)))
        # 嘴唇线
        pygame.draw.line(surf, self.C_DARK, p(2, 17), p(8, 17),
                         max(1, int(1*s)))

        # ── 耳朵 ─────────────────────────────────────────────────
        ear = [p(14, 4), p(17, -4), p(22, 4)]
        pygame.draw.polygon(surf, self.C_BODY, ear)
        pygame.draw.polygon(surf, self.C_DARK,  ear, 1)

        # ── 眼睛 ─────────────────────────────────────────────────
        pygame.draw.circle(surf, self.C_EYE,    p(17, 8), max(1, int(3*s)))
        pygame.draw.circle(surf, (255, 255, 255), p(16, 7), max(1, int(1*s)))

        # ── 鬃毛（沿颈顶） ───────────────────────────────────────
        for i in range(5):
            x1 = 21 + i * 3
            pygame.draw.line(surf, self.C_MANE,
                             p(x1,     2 + i),
                             p(x1 - 4, 10 + i * 2),
                             max(1, int(2*s)))

    # ── 重置（复用对象） ──────────────────────────────────────────
    def respawn(self) -> None:
        self.x = float(self.screen_w + self._W + 10)
        self.active = True
        self.frame = 0
        self._ft = 0
