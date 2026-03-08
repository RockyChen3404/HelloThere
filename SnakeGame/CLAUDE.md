# 贪吃蛇游戏

## 项目概述

基于 Python 实现的经典贪吃蛇游戏。

## 技术栈

- **语言**: Python 3.x
- **GUI 库**: `pygame`（推荐）或 `tkinter`（标准库）
- **包管理**: `pip` / `venv`

## 项目结构

```
贪吃蛇游戏/
├── CLAUDE.md
├── requirements.txt
├── main.py          # 游戏入口
├── game.py          # 游戏主逻辑
├── snake.py         # 蛇的类定义
├── food.py          # 食物的类定义
└── settings.py      # 游戏配置常量
```

## 开发环境设置

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

## 游戏规则

- 使用方向键（↑ ↓ ← →）或 WASD 控制蛇的移动方向
- 蛇吃到食物后身体变长，得分增加
- 蛇撞到墙壁或自身则游戏结束
- 吃到的食物越多，移动速度越快

## 核心模块说明

- **`settings.py`**: 定义屏幕尺寸、颜色、速度等常量
- **`snake.py`**: 蛇的移动、增长、碰撞检测逻辑
- **`food.py`**: 食物的随机生成逻辑
- **`game.py`**: 游戏主循环、分数、状态管理
- **`main.py`**: 程序入口，初始化并启动游戏

## 常用命令

```bash
# 运行游戏
python main.py

# 安装依赖
pip install pygame

# 冻结依赖
pip freeze > requirements.txt

# 运行测试（如有）
python -m pytest
```

## 编码规范

- 遵循 PEP 8 代码风格
- 使用类型注解（Python 3.5+）
- 类名使用 `PascalCase`，函数和变量使用 `snake_case`
- 常量使用全大写 `UPPER_CASE`
