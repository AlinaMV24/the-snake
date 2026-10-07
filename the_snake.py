
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
        """Инициализирует объект с позицией в центре экрана.

        :param body_color: RGB-кортеж цвета объекта.
        """
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.position = (start_x, start_y)
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.

        Базовая реализация ничего не делает.
        Переопределяется в классах-наследниках.
        """
        pass


class Apple(GameObject):
    """Класс яблока — цели для змейки."""

    def __init__(self, body_color=APPLE_COLOR):
        """Инициализирует яблоко и задаёт ему случайную позицию.

        :param body_color: RGB-кортеж цвета яблока.
        """
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self):
        """Перемещает яблоко в случайную клетку игрового поля."""
        x_cell = random.randint(0, GRID_WIDTH - 1)
        y_cell = random.randint(0, GRID_HEIGHT - 1)
        x = x_cell * GRID_SIZE
        y = y_cell * GRID_SIZE
        self.position = (x, y)

    def draw(self):
        """Отрисовывает яблоко как квадрат с обводкой.

        :return: Rect отрисованной ячейки для partial update.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        return rect


class Snake(GameObject):
    """Класс змейки — управляемого игроком объекта."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в центре экрана длиной в одну клетку.

        :param body_color: RGB-кортеж цвета змейки.
        """
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = self.direction
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self):
        """Применяет сохранённое next_direction к direction."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает изменившиеся сегменты и затирает хвост.

        :return: Список Rect, которые нужно обновить на экране.
        """
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        dirty_rects = [head_rect]

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
        """Сдвигает змейку на одну клетку в текущем направлении."""
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
        """Сбрасывает змейку в начальное состояние после проигрыша."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = self.direction
        self.last = None


def handle_keys(game_object):
    """Обрабатывает события клавиатуры и окна.

    При нажатии стрелок задаёт next_direction у змейки,
    запрещая разворот на 180°.

    :param game_object: объект змейки (Snake).
    :return: True — игра продолжается, False — окно закрыто.
    """
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
    """Запускает игровой цикл."""
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
