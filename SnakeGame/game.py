"""
game.py —— 游戏主控制器（生日 · 网球特别版）

生日启动画面特效：
  · 天蓝→草绿渐变明亮背景
  · 白云缓缓飘移
  · 阳光（旋转光芒）
  · 彩虹弹跳字母标题
  · 远远的圆形纪念照（上下浮动）
  · 7 个物理弹跳网球
  · 马年奔跑骏马
  · 缤纷彩带粒子
游戏内网球元素：
  · 食物 = 旋转网球（见 food.py）
  · 游戏背景 = 深色网球硬地绿
  · 中线 = 球场虚线网线
"""
from __future__ import annotations

import math
import os
import random
from enum import Enum, auto
from typing import Any

import pygame

import settings
from horse import Horse
from snake import Snake
from food import Food
from tennis_ball import BouncingTennisBall

try:
    from make_birthday_assets import make_birthday_photo as _make_photo
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False


# ════════════════════════════════════════════════════════════════════
class State(Enum):
    BIRTHDAY  = auto()
    READY     = auto()
    PLAYING   = auto()
    PAUSED    = auto()
    GAME_OVER = auto()


# ════════════════════════════════════════════════════════════════════
class Game:

    # ── 初始化 ────────────────────────────────────────────────────
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self._load_fonts()
        self._load_birthday_assets()
        self.best: int = 0
        self.reset()
        self._start_birthday_screen()

    def _load_fonts(self) -> None:
        pygame.font.init()
        for name in ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                     "SimHei", "WenQuanYi Micro Hei", "Arial Unicode MS"]:
            if pygame.font.match_font(name):
                self._fname = name
                break
        else:
            self._fname = None
        F = self._fname
        self.font_hud    = pygame.font.SysFont(F, 22, bold=True)
        self.font_large  = pygame.font.SysFont(F, 46, bold=True)
        self.font_medium = pygame.font.SysFont(F, 30, bold=True)
        self.font_small  = pygame.font.SysFont(F, 22)
        self.font_tiny   = pygame.font.SysFont(F, 17)

    def _load_birthday_assets(self) -> None:
        photo_path = os.path.join(os.path.dirname(__file__), "by_birthday.png")
        src_path   = os.path.join(os.path.dirname(__file__), "by.jpg")
        if not os.path.exists(photo_path) and _HAS_PILLOW and os.path.exists(src_path):
            try:
                _make_photo(src_path, photo_path)
            except Exception:
                pass
        self.bd_photo: pygame.Surface | None = None
        if os.path.exists(photo_path):
            raw = pygame.image.load(photo_path).convert_alpha()
            rw, rh = raw.get_size()
            nh = 195
            self.bd_photo = pygame.transform.smoothscale(raw, (int(rw * nh / rh), nh))

        # 预渲染渐变背景（天蓝→草绿）
        self._bd_bg = self._make_gradient_bg(
            settings.BD_BG_TOP, settings.BD_BG_BOTTOM,
            settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT,
        )

    @staticmethod
    def _make_gradient_bg(top: tuple, bot: tuple, w: int, h: int) -> pygame.Surface:
        surf = pygame.Surface((w, h))
        for y in range(h):
            t = y / h
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
        return surf

    # ── 游戏重置 ──────────────────────────────────────────────────
    def reset(self) -> None:
        self.snake  = Snake()
        self.food   = Food()
        self.food.spawn(self.snake.body)
        self.score: int  = 0
        self.speed: int  = settings.FPS
        self.eaten: int  = 0
        self.state: State = State.READY
        self._confetti: list[list[Any]] = []

    # ── 生日画面初始化 ────────────────────────────────────────────
    def _start_birthday_screen(self) -> None:
        self.state       = State.BIRTHDAY
        self._bd_start   = pygame.time.get_ticks()
        self._bd_dur     = 18_000           # 18 秒自动进入 READY
        self._bd_tick    = 0

        # 彩带
        self._spawn_confetti(88, bright=True)

        # 云朵  [x, y, speed, scale]
        sw = settings.SCREEN_WIDTH
        self._clouds: list[list[float]] = [
            [  0.0,  65.0, 0.38, 1.00],
            [230.0,  38.0, 0.22, 1.25],
            [460.0,  72.0, 0.30, 0.82],
            [sw + 70.0, 52.0, 0.27, 1.10],
        ]

        # 弹跳网球（在画面下半区初始化）
        sh = settings.SCREEN_HEIGHT
        self._t_balls: list[BouncingTennisBall] = [
            BouncingTennisBall(sw, sh, r=16, y_min=sh // 2)
            for _ in range(7)
        ]

        # 骏马
        self._horse = Horse(
            screen_w=sw,
            y=sh - 90,
            scale=1.45,
            speed=3.4,
        )

    # ════════════════════════════════════════════════════════════════
    # 主循环
    # ════════════════════════════════════════════════════════════════
    def run(self) -> None:
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(settings.FPS)

    # ── 事件 ──────────────────────────────────────────────────────
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self._quit()
                if self.state == State.BIRTHDAY:
                    if event.key not in (pygame.K_ESCAPE, pygame.K_q):
                        self.state = State.READY
                elif self.state == State.READY:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = State.PLAYING
                elif self.state == State.PLAYING:
                    if event.key == pygame.K_p:
                        self.state = State.PAUSED
                    else:
                        self.snake.handle_key(event.key)
                elif self.state == State.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = State.PLAYING
                elif self.state == State.GAME_OVER:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        self.state = State.PLAYING

    # ── 更新 ──────────────────────────────────────────────────────
    def _update(self) -> None:
        if self.state == State.BIRTHDAY:
            self._upd_birthday()
        elif self.state == State.PLAYING:
            self._upd_game()

    def _upd_birthday(self) -> None:
        self._bd_tick += 1
        self._update_confetti()
        for c in self._clouds:          # 云朵向左漂
            c[0] -= c[2]
            if c[0] < -165:
                c[0] = float(settings.SCREEN_WIDTH + 90)
        for tb in self._t_balls:        # 网球物理
            tb.update()
        if self._horse:                  # 骏马
            self._horse.update()
            if not self._horse.active:
                self._horse.respawn()
        if pygame.time.get_ticks() - self._bd_start > self._bd_dur:
            self.state = State.READY

    def _upd_game(self) -> None:
        self.snake.move()
        self.food.update()
        if self.snake.is_dead():
            if self.score > self.best:
                self.best = self.score
            self.state = State.GAME_OVER
            return
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += settings.SCORE_PER_FOOD
            self.eaten += 1
            self.food.spawn(self.snake.body)
            if self.eaten % 5 == 0:
                self.speed = min(self.speed + settings.SPEED_INCREMENT,
                                 settings.SPEED_MAX)

    # ════════════════════════════════════════════════════════════════
    # 彩带粒子
    # ════════════════════════════════════════════════════════════════
    def _spawn_confetti(self, n: int = 60, bright: bool = False) -> None:
        cols = settings.CONFETTI_BD_COLORS if bright else settings.CONFETTI_COLORS
        for _ in range(n):
            self._confetti.append([
                random.randint(0, settings.SCREEN_WIDTH),
                random.randint(-320, -5),
                random.uniform(-0.8, 0.8),       # vx
                random.uniform(2.2, 5.2),        # vy
                random.choice(cols),
                random.randint(5, 12),           # size
                random.uniform(0, 360),          # angle
                random.uniform(-5.5, 5.5),       # spin
                random.choice(["circle", "rect", "diamond"]),
            ])

    def _update_confetti(self) -> None:
        for p in self._confetti:
            p[0] += p[2]; p[1] += p[3]
            p[6] = (p[6] + p[7]) % 360
        self._confetti = [p for p in self._confetti
                          if p[1] < settings.SCREEN_HEIGHT + 15]
        if len(self._confetti) < 65:
            self._spawn_confetti(12, bright=(self.state == State.BIRTHDAY))

    def _draw_confetti(self) -> None:
        for x, y, _, _, color, size, angle, _, shape in self._confetti:
            ix, iy = int(x), int(y)
            if shape == "circle":
                pygame.draw.circle(self.screen, color, (ix, iy), size // 2)
            elif shape == "rect":
                rad = math.radians(angle)
                hw, hh = size, size // 2
                pts_f = [
                    (ix + hw*math.cos(rad) - hh*math.sin(rad),
                     iy + hw*math.sin(rad) + hh*math.cos(rad)),
                    (ix - hw*math.cos(rad) - hh*math.sin(rad),
                     iy - hw*math.sin(rad) + hh*math.cos(rad)),
                    (ix - hw*math.cos(rad) + hh*math.sin(rad),
                     iy - hw*math.sin(rad) - hh*math.cos(rad)),
                    (ix + hw*math.cos(rad) + hh*math.sin(rad),
                     iy + hw*math.sin(rad) - hh*math.cos(rad)),
                ]
                try:
                    pygame.draw.polygon(self.screen, color,
                                        [(int(a), int(b)) for a, b in pts_f])
                except Exception:
                    pass
            else:  # diamond
                pygame.draw.polygon(self.screen, color,
                                    [(ix, iy-size), (ix+size, iy),
                                     (ix, iy+size), (ix-size, iy)])

    # ════════════════════════════════════════════════════════════════
    # 生日专属绘制元素
    # ════════════════════════════════════════════════════════════════

    # ── 太阳（旋转光芒） ──────────────────────────────────────────
    def _draw_sun(self, x: int, y: int, r: int = 38) -> None:
        tick = self._bd_tick
        # 发光光晕（多层半透明）
        for i in range(4, 0, -1):
            glow_surf = pygame.Surface((r*2+i*14, r*2+i*14), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 240, 100, 30),
                               (r+i*7, r+i*7), r+i*7)
            self.screen.blit(glow_surf, (x-r-i*7, y-r-i*7))
        # 光芒（缓慢旋转）
        for i in range(16):
            ang = math.radians(i * 22.5 + tick * 0.8)
            r1 = r + 6 + (4 if i % 2 == 0 else 0)
            r2 = r + 18 + (5 if i % 2 == 0 else 0)
            pygame.draw.line(self.screen, (255, 210, 0),
                             (x + int(r1*math.cos(ang)), y + int(r1*math.sin(ang))),
                             (x + int(r2*math.cos(ang)), y + int(r2*math.sin(ang))),
                             2 if i % 2 == 0 else 1)
        pygame.draw.circle(self.screen, (255, 235, 60), (x, y), r)
        pygame.draw.circle(self.screen, (255, 210,  0), (x, y), r, 2)
        # 笑脸
        pygame.draw.circle(self.screen, (200, 120, 0), (x-10, y-8), 4)
        pygame.draw.circle(self.screen, (200, 120, 0), (x+10, y-8), 4)
        pygame.draw.arc(self.screen, (180, 100, 0),
                        pygame.Rect(x-12, y-4, 24, 16), 0, math.pi, 3)

    # ── 云朵 ──────────────────────────────────────────────────────
    def _draw_cloud(self, x: float, y: float, scale: float = 1.0) -> None:
        s = scale
        blobs = [(0, 0, 52, 34), (-30, 13, 44, 30),
                 (30, 11, 46, 30), (-13,-18, 40, 34), (18,-15, 42, 30)]
        cw, ch = int(140*s), int(92*s)
        cs = pygame.Surface((cw, ch), pygame.SRCALPHA)
        for dx, dy, bw, bh in blobs:
            pygame.draw.ellipse(cs, (255, 255, 255, 215),
                                (int((70+dx-bw//2)*s), int((58+dy-bh//2)*s),
                                 int(bw*s), int(bh*s)))
        self.screen.blit(cs, (int(x - 70*s), int(y - 58*s)))

    def _draw_clouds(self) -> None:
        for cx, cy, _, sc in self._clouds:
            self._draw_cloud(cx, cy, sc)

    # ── 彩虹弹跳字母标题 ──────────────────────────────────────────
    def _draw_bouncy_title(self, text: str, y_base: int) -> None:
        COLORS = [
            (210,  20,  20),   # 红
            (255, 140,   0),   # 橙
            (  0, 165,   0),   # 绿
            (  0, 100, 230),   # 蓝
            (155,   0, 220),   # 紫
            (215,   0, 130),   # 粉
            (190, 155,   0),   # 金
            (  0, 155, 155),   # 青
        ]
        surfs = [self.font_large.render(ch, True, COLORS[i % len(COLORS)])
                 for i, ch in enumerate(text)]
        total_w = sum(s.get_width() + 1 for s in surfs)
        x = (settings.SCREEN_WIDTH - total_w) // 2
        tick = self._bd_tick
        for i, (surf, ch) in enumerate(zip(surfs, text)):
            # 独立弹跳节奏（sin 波，不同相位）
            bounce = int(13 * math.sin(tick * 0.22 + i * 0.62))
            # 描边阴影
            shd = self.font_large.render(ch, True, (60, 28, 0))
            self.screen.blit(shd, (x + 2, y_base - bounce + 3))
            self.screen.blit(surf, (x, y_base - bounce))
            x += surf.get_width() + 1

    # ── 旋转星星爆炸 ──────────────────────────────────────────────
    def _draw_star(self, cx: int, cy: int, r_out: float,
                   r_in: float, color: tuple, angle_off: float = 0) -> None:
        pts: list[tuple[int, int]] = []
        for i in range(10):
            ang = math.radians(angle_off + i * 36)
            r   = r_out if i % 2 == 0 else r_in
            pts.append((cx + int(r * math.cos(ang)),
                        cy + int(r * math.sin(ang))))
        pygame.draw.polygon(self.screen, color, pts)

    def _draw_sparkles(self) -> None:
        """在固定位置绘制缓慢旋转的装饰星。"""
        tick  = self._bd_tick
        SW, SH = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
        stars_config = [
            (55,  45, 12, (255, 220, 0)),
            (SW-55, 45, 10, (255, 100, 160)),
            (30,  SH//2, 9, (100, 200, 255)),
            (SW-30, SH//2, 11, (160, 100, 255)),
            (SW//2 - 240, 130, 8, (255, 160, 0)),
            (SW//2 + 240, 130, 8, (0, 200, 150)),
        ]
        for sx, sy, ro, col in stars_config:
            self._draw_star(sx, sy, ro, ro * 0.42, col, tick * 1.5)

    # ── 生日画面总绘制 ─────────────────────────────────────────────
    def _draw_birthday(self) -> None:
        # 1. 明亮渐变背景
        self.screen.blit(self._bd_bg, (0, 0))

        # 2. 太阳（右上角）
        self._draw_sun(settings.SCREEN_WIDTH - 62, 60)

        # 3. 云朵（背景层）
        self._draw_clouds()

        # 4. 彩带
        self._draw_confetti()

        # 5. 弹跳网球（文字底层）
        for tb in self._t_balls:
            tb.draw(self.screen)

        # 6. 装饰星星
        self._draw_sparkles()

        # 7. 主体内容（标题 / 照片 / 祝福）
        self._draw_bd_content()

        # 8. 骏马（前景底部）
        if self._horse:
            self._horse.draw(self.screen)

        # 9. 闪烁提示
        self._draw_bd_prompt()

    def _draw_bd_content(self) -> None:
        SW = settings.SCREEN_WIDTH
        cx = SW // 2
        tick = self._bd_tick

        # ── 彩虹弹跳标题 ─────────────────────────────────────────
        title = f"生日快乐，{settings.BIRTHDAY_NAME}！"
        self._draw_bouncy_title(title, 52)

        # ── 副标题（半透明白底提高可读性） ───────────────────────
        sub_txt = (f"{settings.BIRTHDAY_DATE}  ·  {settings.BIRTHDAY_AGE}岁"
                   f"  ·  {settings.BIRTHDAY_ZODIAC}大吉  ·  网球小健将🎾")
        sub_s = self.font_tiny.render(sub_txt, True, (30, 80, 20))
        sub_r = sub_s.get_rect(center=(cx, 88))
        pill = sub_r.inflate(22, 10)
        pill_surf = pygame.Surface(pill.size, pygame.SRCALPHA)
        pill_surf.fill((255, 255, 255, 170))
        pygame.draw.rect(pill_surf, (200, 230, 150, 200),
                         pill_surf.get_rect(), 2, border_radius=12)
        self.screen.blit(pill_surf, pill.topleft)
        self.screen.blit(sub_s, sub_r)

        # ── 照片（上下浮动 + 柔光圈） ─────────────────────────────
        PHOTO_TOP = 106
        if self.bd_photo:
            pw, ph = self.bd_photo.get_size()
            px = (SW - pw) // 2
            float_y = int(5 * math.sin(tick * 0.13))

            # 柔光圈
            glow_r = pw // 2 + 18
            glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            for gi in range(8, 0, -1):
                a_val = int(18 * gi)
                pygame.draw.circle(glow_surf, (255, 230, 80, a_val),
                                   (glow_r, glow_r), glow_r - (8 - gi)*2)
            self.screen.blit(glow_surf,
                             (px + pw//2 - glow_r, PHOTO_TOP + ph//2 - glow_r + float_y))

            self.screen.blit(self.bd_photo, (px, PHOTO_TOP + float_y))
            bottom_y = PHOTO_TOP + float_y + ph + 12
        else:
            pygame.draw.circle(self.screen, (210, 230, 255),
                               (cx, PHOTO_TOP + 95), 95)
            bottom_y = PHOTO_TOP + 202

        # ── 祝福卡片 ─────────────────────────────────────────────
        lines = [
            (f"祝{settings.BIRTHDAY_NAME}{settings.BIRTHDAY_AGE}岁生日快乐！", (190, 25, 0)),
            ("愿你每球必进，奔跑如风！", (0, 130, 30)),
        ]
        card_w, card_lh, card_pad = 308, 30, 14
        card_h = len(lines) * card_lh + card_pad * 2
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((255, 255, 255, 185))
        # 动态金边（脉冲亮度）
        pulse = int(200 + 55 * math.sin(tick * 0.18))
        pygame.draw.rect(card_surf, (255, pulse, 0, 230),
                         (0, 0, card_w, card_h), 3, border_radius=12)
        # 小网球装饰
        for bx, col in [(12, (188, 238, 26)), (card_w-12, (188, 238, 26))]:
            pygame.draw.circle(card_surf, col, (bx, card_h//2), 6)
            pygame.draw.circle(card_surf, (255, 255, 255), (bx, card_h//2), 6, 1)
        for i, (txt, col) in enumerate(lines):
            ws = self.font_small.render(txt, True, col)
            wr = ws.get_rect(centerx=card_w//2,
                             y=card_pad + i * card_lh)
            card_surf.blit(ws, wr)
        card_rect = card_surf.get_rect(center=(cx, bottom_y + card_h // 2))
        self.screen.blit(card_surf, card_rect.topleft)

        # ── 网球小图标行（卡片下方） ──────────────────────────────
        icon_y = card_rect.bottom + 12
        for bi in range(9):
            bx = cx - 88 + bi * 22
            by = icon_y + int(4 * math.sin(tick * 0.25 + bi * 0.7))
            pygame.draw.circle(self.screen, (188, 238, 26), (bx, by), 7)
            pygame.draw.circle(self.screen, (255, 255, 255), (bx, by), 7, 1)

    def _draw_bd_prompt(self) -> None:
        if (pygame.time.get_ticks() // 520) % 2 == 0:
            txt = "按任意键开始游戏  ▶"
            ps  = self.font_small.render(txt, True, (20, 80, 20))
            r   = ps.get_rect(center=(settings.SCREEN_WIDTH // 2,
                                      settings.SCREEN_HEIGHT - 20))
            bg  = pygame.Surface((r.width + 28, r.height + 10), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 180))
            pygame.draw.rect(bg, (180, 230, 100, 200),
                             bg.get_rect(), 2, border_radius=10)
            self.screen.blit(bg, (r.left - 14, r.top - 5))
            self.screen.blit(ps, r)

    # ════════════════════════════════════════════════════════════════
    # 游戏画面
    # ════════════════════════════════════════════════════════════════
    def _draw(self) -> None:
        if self.state == State.BIRTHDAY:
            self._draw_birthday()
        else:
            self._draw_game()
        pygame.display.flip()

    def _draw_game(self) -> None:
        self.screen.fill(settings.DARK_GRAY)
        self._draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        self._draw_hud()
        if self.state == State.READY:
            self._draw_overlay("贪  吃  蛇", "按 Enter 或 Space 开始")
        elif self.state == State.PAUSED:
            self._draw_overlay("已  暂  停", "按 P 继续")
        elif self.state == State.GAME_OVER:
            suffix = "  网球小健将继续加油！" if self.score >= 50 else ""
            self._draw_overlay("游 戏 结 束",
                               f"得分：{self.score}{suffix}   Enter 重玩")

    def _draw_grid(self) -> None:
        for x in range(0, settings.SCREEN_WIDTH, settings.CELL_SIZE):
            pygame.draw.line(self.screen, settings.GRID_COLOR,
                             (x, settings.HUD_HEIGHT),
                             (x, settings.SCREEN_HEIGHT))
        for y in range(settings.HUD_HEIGHT,
                       settings.SCREEN_HEIGHT, settings.CELL_SIZE):
            pygame.draw.line(self.screen, settings.GRID_COLOR,
                             (0, y), (settings.SCREEN_WIDTH, y))
        # 球场中线虚线（隐喻球网）
        mid_y  = settings.HUD_HEIGHT + (settings.SCREEN_HEIGHT - settings.HUD_HEIGHT) // 2
        net_col = (32, 82, 55)
        dash, gap = 6, 4
        for x in range(0, settings.SCREEN_WIDTH, dash + gap):
            pygame.draw.line(self.screen, net_col,
                             (x, mid_y),
                             (min(x + dash, settings.SCREEN_WIDTH), mid_y), 1)

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, settings.HUD_BG,
                         (0, 0, settings.SCREEN_WIDTH, settings.HUD_HEIGHT))
        # 小网球图标
        pygame.draw.circle(self.screen, settings.TENNIS_BALL, (22, 20), 9)
        pygame.draw.circle(self.screen, (255, 255, 255), (22, 20), 9, 1)

        items = [
            (f"得分：{self.score}",           settings.SCORE_COLOR, 38),
            (f"最高：{self.best}",             settings.TEXT_COLOR,  200),
            (f"速度：{self.speed}",            settings.TEXT_COLOR,  368),
            (f"长度：{len(self.snake.body)}",  settings.TEXT_COLOR,  508),
        ]
        for text, color, x in items:
            self.screen.blit(self.font_hud.render(text, True, color), (x, 9))

    def _draw_overlay(self, title: str, hint: str) -> None:
        ov = pygame.Surface(
            (settings.SCREEN_WIDTH,
             settings.SCREEN_HEIGHT - settings.HUD_HEIGHT),
            pygame.SRCALPHA)
        ov.fill((0, 0, 0, 168))
        self.screen.blit(ov, (0, settings.HUD_HEIGHT))
        cx = settings.SCREEN_WIDTH  // 2
        cy = (settings.SCREEN_HEIGHT + settings.HUD_HEIGHT) // 2
        shd = self.font_large.render(title, True, (60, 30, 0))
        tit = self.font_large.render(title, True, settings.SCORE_COLOR)
        hnt = self.font_small.render(hint,  True, settings.WHITE)
        self.screen.blit(shd, shd.get_rect(center=(cx+2, cy-28)))
        self.screen.blit(tit, tit.get_rect(center=(cx,   cy-30)))
        self.screen.blit(hnt, hnt.get_rect(center=(cx,   cy+28)))
        if self.state == State.GAME_OVER:
            extra = self.font_small.render(
                f"加油，{settings.BIRTHDAY_NAME}！", True, settings.BD_CYAN)
            self.screen.blit(extra, extra.get_rect(center=(cx, cy + 62)))

    @staticmethod
    def _quit() -> None:
        pygame.quit()
        raise SystemExit
