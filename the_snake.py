import random

import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость игры (FPS)
SPEED = 20

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# ИСПРАВЛЕНИЕ 2: Одинарные кавычки вместо двойных
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Задаёт начальную позицию в центре экрана и цвет объекта.
    Метод draw переопределяется в классах-наследниках.
    """

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        """Инициализирует объект с позицией в центре экрана.

        Args:
            body_color (tuple[int, int, int]): RGB-кортеж цвета объекта.
        """
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране.

        Базовая реализация ничего не делает.
        Переопределяется в классах-наследниках.
        """
        pass


class Apple(GameObject):
    """Класс яблока — цели для змейки.

    Яблоко появляется в случайной клетке поля.
    При съедании змейкой перемещается в новую случайную позицию.
    """

    def __init__(self, body_color=APPLE_COLOR):
        """Инициализирует яблоко и задаёт ему случайную позицию.

        Args:
            body_color (tuple[int, int, int]): RGB-кортеж цвета яблока.
        """
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Перемещает яблоко в случайную клетку игрового поля."""
        while True:
            new_position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if snake_positions is None or new_position not in snake_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовывает яблоко как квадрат с обводкой.

        Returns:
            list[pygame.Rect]: Список с одним прямоугольником яблока.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки — управляемого игроком объекта.

    Змейка состоит из списка сегментов (позиций на сетке).
    Двигается по полю, телепортируясь через границы экрана.
    Растёт при поедании яблок и погибает при столкновении с собой.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в центре экрана длиной в одну клетку.

        Args:
            body_color (tuple[int, int, int]): RGB-кортеж цвета змейки.
        """
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки (первый элемент списка).

        Returns:
            tuple[int, int]: Позиция головы (x, y).
        """
        return self.positions[0]

    def update_direction(self):
        """Применяет сохранённое next_direction к direction.

        Если next_direction не None, копирует его в direction
        и обнуляет next_direction.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает изменившиеся сегменты и затирает хвост."""
        # Рисуем голову
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        Голова вставляется в начало списка positions.
        Если длина списка превышает self.length — хвост удаляется.
        Координаты рассчитываются с телепортацией через границы.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_x = head_x + direction_x * GRID_SIZE
        new_y = head_y + direction_y * GRID_SIZE
        new_x = (new_x + SCREEN_WIDTH) % SCREEN_WIDTH
        new_y = (new_y + SCREEN_HEIGHT) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние после проигрыша."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = self.direction


def handle_keys(game_object):
    """Обрабатывает события клавиатуры и окна.

    При нажатии стрелок задаёт next_direction у змейки,
    запрещая разворот на 180°. При закрытии окна возвращает False.

    Args:
        game_object (Snake): Объект змейки.

    Returns:
        bool: True — игра продолжается, False — окно закрыто.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
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
        # Проверка: змейка съела яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        # Проверка: столкновение с собственным телом (ИСПРАВЛЕНО на elif)
        elif snake.get_head_position() in snake.positions[1:]:
            running = False

        # ПОЛНАЯ очистка экрана и перерисовка каждый кадр
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()

        clock.tick(SPEED)

    pygame.quit()


if __name__ == '__main__':
    main()
