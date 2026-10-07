
import random
import pygame


# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость
SPEED = 20

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=(0, 0, 0)):
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.position = (start_x, start_y)
        self.body_color = body_color

    def draw(self):
        pass


class Apple(GameObject):
    """Класс яблока — цели для змейки."""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self):
        x_cell = random.randint(0, GRID_WIDTH - 1)
        y_cell = random.randint(0, GRID_HEIGHT - 1)
        x = x_cell * GRID_SIZE
        y = y_cell * GRID_SIZE
        self.position = (x, y)

    def draw(self):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        return rect


class Snake(GameObject):
    """Класс змейки — управляемого игроком объекта."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = self.direction
        self.last = None

    def get_head_position(self):
        return self.positions[0]

    def update_direction(self):
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        dirty_rects = []

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        dirty_rects.append(head_rect)

        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            dirty_rects.append(last_rect)

        if len(self.positions) > 1:
            neck_rect = pygame.Rect(self.positions[1], (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, neck_rect)
            pygame.draw.rect(screen, BORDER_COLOR, neck_rect, 1)
            dirty_rects.append(neck_rect)

        return dirty_rects

    def move(self):
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = head_x + dx * GRID_SIZE
        new_y = head_y + dy * GRID_SIZE

        new_x = (new_x + SCREEN_WIDTH) % SCREEN_WIDTH
        new_y = (new_y + SCREEN_HEIGHT) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = self.direction
        self.last = None


def handle_keys(game_object):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT

    return True


def main():
    pygame.init()
    apple = Apple(APPLE_COLOR)
    snake = Snake(SNAKE_COLOR)

    screen.fill(BOARD_BACKGROUND_COLOR)
    apple.draw()
    snake.draw()
    pygame.display.update()

    running = True
    while running:
        running = handle_keys(snake)
        if not running:
            break

        snake.update_direction()
        snake.move()

        dirty_rects = []

        if snake.get_head_position() == apple.position:
            snake.length += 1
            old_apple_rect = pygame.Rect(
                apple.position, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, old_apple_rect
            )
            dirty_rects.append(old_apple_rect)
            apple.randomize_position()
            dirty_rects.append(apple.draw())

        head = snake.get_head_position()
        if head in snake.positions[1:]:
            running = False

        dirty_rects.extend(snake.draw())
        pygame.display.update(dirty_rects)

        clock.tick(SPEED)

    pygame.quit()


if __name__ == '__main__':
    main()
