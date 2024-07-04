import random
import sys

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
        self.running = True
        self.reset()

    def reset(self):
        self.direction = [BLOCK_SIZE, 0]
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

        reward = 0
        if self.snake.check_collision() or self.frame_iteration > 100 * len(self.snake):
            reward = -10
            return self.game_over(), reward, self.score

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.randomize_position()
            self.score += 1
            reward = 10

        return self.running, reward, self.score

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
        print("Game Over!")
        print(f"Your score: {self.score}")
        self.running = False


class Snake:
    def __init__(self):
        self.body = [
            (BLOCK_SIZE * 1, BLOCK_SIZE * 1),
            (BLOCK_SIZE * 2, BLOCK_SIZE * 2),
            (BLOCK_SIZE * 3, BLOCK_SIZE * 3),
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

    def check_collision(self):
        head_x, head_y = self.body[0]
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            return True
        if (head_x, head_y) in self.body[1:]:
            return True
        return False

    def change_direction(self, action):
        if action == "LEFT":
            self.direction = (-BLOCK_SIZE, 0)
        elif action == "RIGHT":
            self.direction = (BLOCK_SIZE, 0)
        elif action == "UP":
            self.direction = (0, -BLOCK_SIZE)
        elif action == "DOWN":
            self.direction = (0, BLOCK_SIZE)


class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.position = (x, y)
        return self.position


def initialize_game():
    pygame.init()
    game = Game()
    return game


def main_loop(game):
    while game.running:
        game.handle_events()
        game.update()
        game.render()
        game.clock.tick(10)

    pygame.quit()


if __name__ == "__main__":
    game = initialize_game()
    main_loop(game)
