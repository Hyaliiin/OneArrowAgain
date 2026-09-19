import pygame
import sys

pygame.init()

# ==================================================
# 窗口设置
# ==================================================
WIDTH = 900
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

# ==================================================
# 颜色
# ==================================================
BACKGROUND = (245, 247, 250)

TITLE_COLOR = (45, 55, 72)
ARROW_COLOR = (50, 60, 80)
GRID_COLOR = (190, 195, 205)

BUTTON_COLOR = (78, 132, 255)
BUTTON_HOVER_COLOR = (55, 110, 235)
BUTTON_TEXT_COLOR = (255, 255, 255)

SUCCESS_COLOR = (50, 150, 90)
ERROR_COLOR = (220, 70, 70)
HINT_COLOR = (45, 180, 105)

# ==================================================
# 字体
# ==================================================
font_path = "C:/Windows/Fonts/msyh.ttc"

title_font = pygame.font.Font(font_path, 64)
normal_font = pygame.font.Font(font_path, 28)
button_font = pygame.font.Font(font_path, 30)
info_font = pygame.font.Font(font_path, 24)

# ==================================================
# 棋盘设置
# ==================================================
ROWS = 5
COLS = 5

CELL_SIZE = 80

BOARD_X = WIDTH // 2 - (COLS * CELL_SIZE) // 2
BOARD_Y = 170

# ==================================================
# 三个关卡
# ==================================================
level_1 = [
    [".", "↑", ".", "→", "."],
    ["←", ".", ".", ".", "↑"],
    [".", ".", "↓", ".", "."],
    ["←", ".", ".", "←", "."],
    [".", "↑", ".", ".", "→"]
]

level_2 = [
    [".", "→", ".", "↑", "↑"],
    [".", ".", "↑", ".", "."],
    [".", ".", "↑", "↑", "↓"],
    ["←", ".", ".", ".", "←"],
    [".", ".", ".", "↑", "→"]
]

level_3 = [
    ["→", ".", "↓", ".", "."],
    ["→", ".", ".", "→", "↓"],
    [".", ".", "↓", ".", "→"],
    ["↓", "←", "←", "←", "↓"],
    [".", "→", "↓", ".", "→"]
]

levels = [
    level_1,
    level_2,
    level_3
]

# ==================================================
# 游戏状态
# ==================================================
game_state = "START"

current_level = 0

MAX_MISTAKES = 3
mistakes_left = MAX_MISTAKES

board = [
    row[:] for row in levels[current_level]
]

# ==================================================
# 按钮
# ==================================================
start_button = pygame.Rect(
    WIDTH // 2 - 120,
    430,
    240,
    70
)

# 游戏界面的两个按钮
hint_button = pygame.Rect(
    WIDTH // 2 - 190,
    610,
    160,
    55
)

restart_button = pygame.Rect(
    WIDTH // 2 + 30,
    610,
    160,
    55
)

retry_button = pygame.Rect(
    WIDTH // 2 - 120,
    430,
    240,
    70
)

next_button = pygame.Rect(
    WIDTH // 2 - 120,
    430,
    240,
    70
)

again_button = pygame.Rect(
    WIDTH // 2 - 120,
    450,
    240,
    70
)

# ==================================================
# 操作反馈
# ==================================================
feedback_text = ""
feedback_until = 0

blocked_cell = None
blocked_until = 0

# ==================================================
# 提示功能
# ==================================================
hint_cell = None
hint_until = 0

# ==================================================
# 飞行动画
# ==================================================
FLY_SPEED = 14
flying_arrow = None


# ==================================================
# 绘制箭头
# ==================================================
def draw_arrow(surface, direction, center, color):

    cx, cy = center

    length = 42
    head_size = 16
    line_width = 7

    if direction == "↑":

        pygame.draw.line(
            surface,
            color,
            (cx, cy + length // 2),
            (cx, cy - length // 2 + 8),
            line_width
        )

        points = [
            (cx, cy - length // 2 - 8),
            (cx - head_size, cy - length // 2 + 10),
            (cx + head_size, cy - length // 2 + 10)
        ]

        pygame.draw.polygon(surface, color, points)

    elif direction == "↓":

        pygame.draw.line(
            surface,
            color,
            (cx, cy - length // 2),
            (cx, cy + length // 2 - 8),
            line_width
        )

        points = [
            (cx, cy + length // 2 + 8),
            (cx - head_size, cy + length // 2 - 10),
            (cx + head_size, cy + length // 2 - 10)
        ]

        pygame.draw.polygon(surface, color, points)

    elif direction == "←":

        pygame.draw.line(
            surface,
            color,
            (cx + length // 2, cy),
            (cx - length // 2 + 8, cy),
            line_width
        )

        points = [
            (cx - length // 2 - 8, cy),
            (cx - length // 2 + 10, cy - head_size),
            (cx - length // 2 + 10, cy + head_size)
        ]

        pygame.draw.polygon(surface, color, points)

    elif direction == "→":

        pygame.draw.line(
            surface,
            color,
            (cx - length // 2, cy),
            (cx + length // 2 - 8, cy),
            line_width
        )

        points = [
            (cx + length // 2 + 8, cy),
            (cx + length // 2 - 10, cy - head_size),
            (cx + length // 2 - 10, cy + head_size)
        ]

        pygame.draw.polygon(surface, color, points)


# ==================================================
# 判断路径是否畅通
# ==================================================
def is_path_clear(row, col):

    direction = board[row][col]

    if direction == "↑":

        for r in range(row - 1, -1, -1):

            if board[r][col] != ".":
                return False

    elif direction == "↓":

        for r in range(row + 1, ROWS):

            if board[r][col] != ".":
                return False

    elif direction == "←":

        for c in range(col - 1, -1, -1):

            if board[row][c] != ".":
                return False

    elif direction == "→":

        for c in range(col + 1, COLS):

            if board[row][c] != ".":
                return False

    return True


# ==================================================
# 查找一个可以飞出的箭头
# ==================================================
def find_hint_arrow():

    for row in range(ROWS):

        for col in range(COLS):

            if board[row][col] != ".":

                if is_path_clear(row, col):

                    return row, col

    return None


# ==================================================
# 统计剩余箭头
# ==================================================
def get_remaining():

    return sum(
        1
        for row_data in board
        for cell in row_data
        if cell != "."
    )


# ==================================================
# 加载关卡
# ==================================================
def load_level(level_index):

    global board
    global mistakes_left

    global feedback_text
    global feedback_until

    global blocked_cell
    global blocked_until

    global hint_cell
    global hint_until

    global flying_arrow

    board = [
        row[:] for row in levels[level_index]
    ]

    mistakes_left = MAX_MISTAKES

    feedback_text = ""
    feedback_until = 0

    blocked_cell = None
    blocked_until = 0

    hint_cell = None
    hint_until = 0

    flying_arrow = None


# ==================================================
# 创建飞行动画
# ==================================================
def create_flying_arrow(row, col, direction):

    x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
    y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

    dx = 0
    dy = 0

    if direction == "↑":
        dy = -FLY_SPEED

    elif direction == "↓":
        dy = FLY_SPEED

    elif direction == "←":
        dx = -FLY_SPEED

    elif direction == "→":
        dx = FLY_SPEED

    return {
        "direction": direction,
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy
    }


# ==================================================
# 判断动画箭头是否离开窗口
# ==================================================
def arrow_outside_window(arrow):

    return (
        arrow["x"] < -70
        or arrow["x"] > WIDTH + 70
        or arrow["y"] < -70
        or arrow["y"] > HEIGHT + 70
    )


# ==================================================
# 绘制普通按钮
# ==================================================
def draw_button(rect, text):

    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER_COLOR
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=15
    )

    text_surface = button_font.render(
        text,
        True,
        BUTTON_TEXT_COLOR
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )


# ==================================================
# 绘制游戏界面的小按钮
# ==================================================
def draw_small_button(rect, text):

    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER_COLOR
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=12
    )

    text_surface = info_font.render(
        text,
        True,
        BUTTON_TEXT_COLOR
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )


# ==================================================
# 游戏主循环
# ==================================================
running = True

while running:

    # ==================================================
    # 事件处理
    # ==================================================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                # ==============================
                # 开始界面
                # ==============================
                if game_state == "START":

                    if start_button.collidepoint(event.pos):

                        current_level = 0

                        load_level(current_level)

                        game_state = "PLAYING"

                # ==============================
                # 游戏界面
                # ==============================
                elif game_state == "PLAYING":

                    # --------------------------
                    # 提示按钮
                    # --------------------------
                    if hint_button.collidepoint(event.pos):

                        if flying_arrow is None:

                            hint_cell = find_hint_arrow()

                            if hint_cell is not None:

                                hint_until = (
                                    pygame.time.get_ticks()
                                    + 1200
                                )

                                feedback_text = (
                                    "绿色箭头可以飞出！"
                                )

                                feedback_until = (
                                    pygame.time.get_ticks()
                                    + 1200
                                )

                    # --------------------------
                    # 重新开始按钮
                    # --------------------------
                    elif restart_button.collidepoint(event.pos):

                        load_level(current_level)

                    # --------------------------
                    # 点击棋盘
                    # --------------------------
                    elif flying_arrow is None:

                        mouse_x, mouse_y = event.pos

                        if (
                            BOARD_X <= mouse_x
                            < BOARD_X + COLS * CELL_SIZE
                            and
                            BOARD_Y <= mouse_y
                            < BOARD_Y + ROWS * CELL_SIZE
                        ):

                            col = (
                                mouse_x - BOARD_X
                            ) // CELL_SIZE

                            row = (
                                mouse_y - BOARD_Y
                            ) // CELL_SIZE

                            if board[row][col] != ".":

                                direction = board[row][col]

                                # 点击箭头后取消提示
                                hint_cell = None

                                # ======================
                                # 路径畅通
                                # ======================
                                if is_path_clear(row, col):

                                    flying_arrow = (
                                        create_flying_arrow(
                                            row,
                                            col,
                                            direction
                                        )
                                    )

                                    board[row][col] = "."

                                    feedback_text = (
                                        "箭头成功飞出！"
                                    )

                                    feedback_until = (
                                        pygame.time.get_ticks()
                                        + 800
                                    )

                                    blocked_cell = None

                                # ======================
                                # 路径被阻挡
                                # ======================
                                else:

                                    mistakes_left -= 1

                                    feedback_text = (
                                        "前方有阻挡！"
                                    )

                                    feedback_until = (
                                        pygame.time.get_ticks()
                                        + 800
                                    )

                                    blocked_cell = (
                                        row,
                                        col
                                    )

                                    blocked_until = (
                                        pygame.time.get_ticks()
                                        + 500
                                    )

                                    if mistakes_left <= 0:

                                        game_state = "LOSE"

                # ==============================
                # 失败界面
                # ==============================
                elif game_state == "LOSE":

                    if retry_button.collidepoint(event.pos):

                        load_level(current_level)

                        game_state = "PLAYING"

                # ==============================
                # 当前关卡通过
                # ==============================
                elif game_state == "LEVEL_CLEAR":

                    if next_button.collidepoint(event.pos):

                        current_level += 1

                        load_level(current_level)

                        game_state = "PLAYING"

                # ==============================
                # 全部通关
                # ==============================
                elif game_state == "ALL_CLEAR":

                    if again_button.collidepoint(event.pos):

                        current_level = 0

                        load_level(current_level)

                        game_state = "PLAYING"

    # ==================================================
    # 更新飞行动画
    # ==================================================
    if (
        game_state == "PLAYING"
        and flying_arrow is not None
    ):

        flying_arrow["x"] += flying_arrow["dx"]
        flying_arrow["y"] += flying_arrow["dy"]

        if arrow_outside_window(flying_arrow):

            flying_arrow = None

            if get_remaining() == 0:

                if current_level == len(levels) - 1:

                    game_state = "ALL_CLEAR"

                else:

                    game_state = "LEVEL_CLEAR"

    # ==================================================
    # 绘制背景
    # ==================================================
    screen.fill(BACKGROUND)

    # ==================================================
    # 开始界面
    # ==================================================
    if game_state == "START":

        title = title_font.render(
            "一箭又一箭",
            True,
            TITLE_COLOR
        )

        title_rect = title.get_rect(
            center=(WIDTH // 2, 190)
        )

        screen.blit(
            title,
            title_rect
        )

        description = normal_font.render(
            "点击箭头，让所有箭头飞出棋盘！",
            True,
            (100, 105, 115)
        )

        description_rect = description.get_rect(
            center=(WIDTH // 2, 300)
        )

        screen.blit(
            description,
            description_rect
        )

        draw_button(
            start_button,
            "开始游戏"
        )

    # ==================================================
    # 游戏界面
    # ==================================================
    elif game_state == "PLAYING":

        # 当前关卡
        level_text = normal_font.render(
            f"第 {current_level + 1} 关",
            True,
            TITLE_COLOR
        )

        screen.blit(
            level_text,
            (80, 55)
        )

        # 剩余箭头
        remaining_text = info_font.render(
            f"剩余箭头：{get_remaining()}",
            True,
            TITLE_COLOR
        )

        screen.blit(
            remaining_text,
            (WIDTH - 250, 55)
        )

        # 剩余失误
        mistake_text = info_font.render(
            f"剩余失误：{mistakes_left}",
            True,
            TITLE_COLOR
        )

        screen.blit(
            mistake_text,
            (WIDTH - 250, 95)
        )

        # ==================================================
        # 操作反馈
        # ==================================================
        if (
            feedback_text
            and pygame.time.get_ticks()
            < feedback_until
        ):

            if feedback_text == "前方有阻挡！":

                feedback_color = ERROR_COLOR

            elif feedback_text == "绿色箭头可以飞出！":

                feedback_color = HINT_COLOR

            else:

                feedback_color = SUCCESS_COLOR

            feedback_surface = info_font.render(
                feedback_text,
                True,
                feedback_color
            )

            feedback_rect = feedback_surface.get_rect(
                center=(WIDTH // 2, 125)
            )

            screen.blit(
                feedback_surface,
                feedback_rect
            )

        # ==================================================
        # 绘制棋盘
        # ==================================================
        for row in range(ROWS):

            for col in range(COLS):

                x = (
                    BOARD_X
                    + col * CELL_SIZE
                )

                y = (
                    BOARD_Y
                    + row * CELL_SIZE
                )

                cell_rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )

                pygame.draw.rect(
                    screen,
                    GRID_COLOR,
                    cell_rect,
                    2
                )

                cell = board[row][col]

                if cell != ".":

                    arrow_color = ARROW_COLOR

                    arrow_center = list(
                        cell_rect.center
                    )

                    # ==========================
                    # 提示箭头绿色闪烁
                    # ==========================
                    if (
                        hint_cell == (row, col)
                        and pygame.time.get_ticks()
                        < hint_until
                    ):

                        flash_phase = (
                            pygame.time.get_ticks()
                            // 150
                        ) % 2

                        if flash_phase == 0:
                            arrow_color = HINT_COLOR

                    # ==========================
                    # 碰撞箭头红色晃动
                    # ==========================
                    if (
                        blocked_cell == (row, col)
                        and pygame.time.get_ticks()
                        < blocked_until
                    ):

                        arrow_color = ERROR_COLOR

                        shake_phase = (
                            pygame.time.get_ticks()
                            // 45
                        ) % 2

                        if shake_phase == 0:
                            arrow_center[0] -= 6
                        else:
                            arrow_center[0] += 6

                    draw_arrow(
                        screen,
                        cell,
                        arrow_center,
                        arrow_color
                    )

        # ==================================================
        # 飞行中的箭头
        # ==================================================
        if flying_arrow is not None:

            draw_arrow(
                screen,
                flying_arrow["direction"],
                (
                    int(flying_arrow["x"]),
                    int(flying_arrow["y"])
                ),
                SUCCESS_COLOR
            )

        # ==================================================
        # 游戏按钮
        # ==================================================
        draw_small_button(
            hint_button,
            "提示"
        )

        draw_small_button(
            restart_button,
            "重新开始"
        )

    # ==================================================
    # 失败界面
    # ==================================================
    elif game_state == "LOSE":

        lose_title = title_font.render(
            "挑战失败",
            True,
            ERROR_COLOR
        )

        lose_title_rect = lose_title.get_rect(
            center=(WIDTH // 2, 220)
        )

        screen.blit(
            lose_title,
            lose_title_rect
        )

        lose_tip = normal_font.render(
            "失误次数已经用完，再试一次吧！",
            True,
            TITLE_COLOR
        )

        lose_tip_rect = lose_tip.get_rect(
            center=(WIDTH // 2, 320)
        )

        screen.blit(
            lose_tip,
            lose_tip_rect
        )

        draw_button(
            retry_button,
            "重新挑战"
        )

    # ==================================================
    # 单关通关
    # ==================================================
    elif game_state == "LEVEL_CLEAR":

        win_title = title_font.render(
            "挑战成功！",
            True,
            SUCCESS_COLOR
        )

        win_title_rect = win_title.get_rect(
            center=(WIDTH // 2, 210)
        )

        screen.blit(
            win_title,
            win_title_rect
        )

        win_text = normal_font.render(
            f"第 {current_level + 1} 关已完成",
            True,
            TITLE_COLOR
        )

        win_text_rect = win_text.get_rect(
            center=(WIDTH // 2, 320)
        )

        screen.blit(
            win_text,
            win_text_rect
        )

        draw_button(
            next_button,
            "下一关"
        )

    # ==================================================
    # 全部通关
    # ==================================================
    elif game_state == "ALL_CLEAR":

        all_title = title_font.render(
            "全部通关！",
            True,
            SUCCESS_COLOR
        )

        all_title_rect = all_title.get_rect(
            center=(WIDTH // 2, 200)
        )

        screen.blit(
            all_title,
            all_title_rect
        )

        all_text = normal_font.render(
            "恭喜你完成了全部 3 个关卡！",
            True,
            TITLE_COLOR
        )

        all_text_rect = all_text.get_rect(
            center=(WIDTH // 2, 315)
        )

        screen.blit(
            all_text,
            all_text_rect
        )

        draw_button(
            again_button,
            "再玩一次"
        )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()