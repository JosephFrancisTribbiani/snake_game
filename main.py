from _collections import deque
import pygame
import sys
from random import randint

H_BLOCKS_QTY = 15
V_BLOCKS_QTY = 10
BLOCK_SIZE = 20
MARGIN = 1
WALL_THICK = 5
TEXT_SIZE = 36
BANNER_THICK = 10*3 + TEXT_SIZE*2
LEVEL_STAGE = 5

FRAME_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (50, 50, 50)
SNAKE_COLOR = (0, 100, 0)
APPLE_COLOR = (224, 0, 0)


class Move:
    DOWN = (0, 1)
    RIGHT = (1, 0)
    UP = (0, -1)
    LEFT = (-1, 0)

    MOVES = (DOWN, RIGHT, UP, LEFT)


class SnakeScreen:
    def __init__(self,
                 height=BANNER_THICK + WALL_THICK * 2 + BLOCK_SIZE * V_BLOCKS_QTY + MARGIN * (V_BLOCKS_QTY - 1),
                 width=WALL_THICK * 2 + BLOCK_SIZE * H_BLOCKS_QTY + MARGIN * (H_BLOCKS_QTY - 1)):
        self.surface = pygame.display.set_mode(size=[width, height])
        pygame.display.set_caption("Snake Game")

    def draw_playing_field(self, scr, lvl):
        head_font = pygame.font.SysFont("Bauhaus 93", TEXT_SIZE)
        text_score = head_font.render(f"SCORE: {scr}", 1, WHITE)
        text_level = head_font.render(f"LEVEL: {lvl}", 1, WHITE)
        self.surface.fill(FRAME_COLOR)
        # left, top, width, height
        pygame.draw.rect(self.surface,
                         WALL_COLOR,
                         [0,
                          BANNER_THICK,
                          WALL_THICK * 2 + BLOCK_SIZE * H_BLOCKS_QTY + MARGIN * (H_BLOCKS_QTY - 1),
                          WALL_THICK * 2 + BLOCK_SIZE * H_BLOCKS_QTY + MARGIN * (H_BLOCKS_QTY - 1)])
        pygame.draw.rect(self.surface,
                         FRAME_COLOR,
                         [WALL_THICK,
                          BANNER_THICK + WALL_THICK,
                          BLOCK_SIZE * H_BLOCKS_QTY + MARGIN * (H_BLOCKS_QTY - 1),
                          BLOCK_SIZE * V_BLOCKS_QTY + MARGIN * (V_BLOCKS_QTY - 1)])
        self.surface.blit(text_score, (10, 10))
        self.surface.blit(text_level, (10, 10*2 + TEXT_SIZE))

    def draw_apple(self, apple):
        pygame.draw.rect(self.surface,
                         APPLE_COLOR,
                         [WALL_THICK + apple.x * (BLOCK_SIZE + MARGIN),
                          WALL_THICK + BANNER_THICK + apple.y * (BLOCK_SIZE + MARGIN),
                          BLOCK_SIZE,
                          BLOCK_SIZE])

    def draw_snake(self, snake):
        for block in snake:
            pygame.draw.rect(self.surface,
                             SNAKE_COLOR,
                             [WALL_THICK + block.x * (BLOCK_SIZE + MARGIN),
                              WALL_THICK + BANNER_THICK + block.y * (BLOCK_SIZE + MARGIN),
                              BLOCK_SIZE,
                              BLOCK_SIZE])


class SnakeBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, SnakeBlock) and self.x == other.x and self.y == other.y

    def is_inside(self):
        return 0 <= self.x < H_BLOCKS_QTY and 0 <= self.y < V_BLOCKS_QTY


def get_random_empty_block(snake):
    field = [[0] * H_BLOCKS_QTY for _ in range(V_BLOCKS_QTY)]
    visited = [[False] * H_BLOCKS_QTY for _ in range(V_BLOCKS_QTY)]
    q = deque()  # (x, y)
    q.append((randint(0, H_BLOCKS_QTY - 1), randint(0, V_BLOCKS_QTY - 1)))

    for elem in snake:
        field[elem.y][elem.x] = 1

    while len(q) > 0:
        x, y = q.popleft()
        visited[y][x] = True

        if not field[y][x]:
            return SnakeBlock(x, y)

        for d_x, d_y in Move.MOVES:
            new_x, new_y = x + d_x, y + d_y
            if 0 <= new_x < H_BLOCKS_QTY and 0 <= new_y < V_BLOCKS_QTY and not visited[new_y][new_x]:
                q.append((new_x, new_y))
                visited[new_y][new_x] = True
    return None


def main():
    timer = pygame.time.Clock()
    d_r, d_c = 0, 1
    score = 0
    level = pre_level = 1

    # создаем интерфейс игрового поля
    screen = SnakeScreen()
    screen.draw_playing_field(score, level)

    # создаем змейку (список ее блоков)
    snake = deque([SnakeBlock(H_BLOCKS_QTY // 2, V_BLOCKS_QTY // 2)])

    # получаем координаты положения яблока
    apple = get_random_empty_block(snake)

    # отрисовываем змейку на экране
    screen.draw_snake(snake)

    while True:
        head_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not head_moved:
                if event.key == pygame.K_UP and d_c != 0:
                    d_r, d_c = -1, 0
                elif event.key == pygame.K_DOWN and d_c != 0:
                    d_r, d_c = 1, 0
                elif event.key == pygame.K_RIGHT and d_r != 0:
                    d_r, d_c = 0, 1
                elif event.key == pygame.K_LEFT and d_r != 0:
                    d_r, d_c = 0, - 1
                head_moved = True

        # получаем новое положение головы змейки и убираем хвост
        new_head = SnakeBlock(snake[-1].x + d_c, snake[-1].y + d_r)
        snake.popleft()

        # проверяем что если новое положение головы за пределами поля, то выходим из игры
        if not new_head.is_inside() or new_head in snake:
            # запускаем звуковой эффект
            file = 'sounds/crash.mp3'
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(1)

            # и выходим из игры
            pygame.quit()
            sys.exit()

        # двигаем нашу змейку
        snake.append(new_head)

        if new_head == apple:
            # добавляем очки и размещаем яблоко в новое место
            score += 1
            level = score // LEVEL_STAGE + 1
            snake.append(apple)
            apple = get_random_empty_block(snake)

            # запускаем звуковой эффект
            if level > pre_level:
                pre_level = level
                file = 'sounds/level_up.mp3'
            else:
                file = 'sounds/apple.mp3'
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()

        # обновляем изменения на экране
        screen.draw_playing_field(score, level)
        screen.draw_apple(apple)
        screen.draw_snake(snake)
        pygame.display.flip()
        timer.tick(2 + level)


if __name__ == '__main__':
    pygame.init()
    main()
