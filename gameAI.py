import random

import numpy as np
import pygame

WIDTH = 400
HEIGHT = 400
BLOCK_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.reward = 0
        self.running = True
        self.reset()

    def reset(self):
        self.snake.direction = [BLOCK_SIZE, 0]
        self.body = [
            (BLOCK_SIZE * 1, BLOCK_SIZE * 1),
            (BLOCK_SIZE * 2, BLOCK_SIZE * 2),
            (BLOCK_SIZE * 3, BLOCK_SIZE * 3),
        ]
        self.score = 0
        self.food.randomize_position()
        self.frame_iteration = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.snake.change_direction()

    def update(self, action):
        if not self.running:
            return

        self.frame_iteration += 1

        self.snake.move(action)

        self.reward = 0

        if self.snake.check_collision() or self.frame_iteration > 100 * len(self.snake):
            self.reward = -10
            self.get_game_state()

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.randomize_position()
            self.score += 1
            self.reward = 10

        self.get_game_state()

    def render(self):
        self.screen.fill(BLACK)
        for segment in self.snake.body:
            pygame.draw.rect(
                self.screen,
                GREEN,
                pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE),
            )
        pygame.draw.rect(
            self.screen,
            BLUE,
            pygame.Rect(
                self.food.position[0], self.food.position[1], BLOCK_SIZE, BLOCK_SIZE
            ),
        )
        font = pygame.font.Font(None, 25)
        text = font.render(f"Score {str(self.score)}", True, WHITE)
        self.screen.blit(text, [0, 0])
        pygame.display.flip()

    def game_over(self):
        self.running = False

    def get_game_state(self):
        return self.reward, self.running, self.score

    def get_snake_state(self):
        head = self.snake.body[0]

        point_l = (head[0] - 20, head[1])
        point_r = (head[0] + 20, head[1])
        point_u = (head[0], head[1] - 20)
        point_d = (head[0], head[1] + 20)

        dir_l = self.snake.direction == [-20, 0]
        dir_r = self.snake.direction == [20, 0]
        dir_u = self.snake.direction == [0, -20]
        dir_d = self.snake.direction == [0, 20]

        state = [
            (dir_r and self.snake.check_collision(point_r))
            or (dir_l and self.snake.check_collision(point_l))
            or (dir_u and self.snake.check_collision(point_u))
            or (dir_d and self.snake.check_collision(point_d)),
            (dir_u and self.snake.check_collision(point_r))
            or (dir_d and self.snake.check_collision(point_l))
            or (dir_l and self.snake.check_collision(point_u))
            or (dir_r and self.snake.check_collision(point_d)),
            (dir_d and self.snake.check_collision(point_r))
            or (dir_u and self.snake.check_collision(point_l))
            or (dir_r and self.snake.check_collision(point_u))
            or (dir_l and self.snake.check_collision(point_d)),
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            self.food.position[0] < head[0],
            self.food.position[0] > head[0],
            self.food.position[1] < head[1],
            self.food.position[1] < head[1],
        ]

        return np.array(state, dtype=int)


class Snake:
    def __init__(self):
        self.body = [
            (BLOCK_SIZE * 3, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 2, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 1, BLOCK_SIZE * 5),
        ]
        self.direction = [BLOCK_SIZE, 0]

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (
            head_x + self.direction[0],
            head_y + self.direction[1],
        )
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.body.append(self.body[-1])

    def check_collision(self, pt):
        if pt is None:
            pt = self.body[0]
        if pt[0] < 0 or pt[0] >= WIDTH or pt[1] < 0 or pt[1] >= HEIGHT:
            return True
        if pt in self.body[1:]:
            return True
        return False

    def change_direction(self, action):
        # [straight, right, left]

        clock_wise = [
            [BLOCK_SIZE, 0],
            [0, BLOCK_SIZE],
            [-BLOCK_SIZE, 0],
            [0, -BLOCK_SIZE],
        ]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir


class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.position = (x, y)
        return self.position
