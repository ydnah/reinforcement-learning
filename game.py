import random
import sys

import pygame

WIDTH = 800
HEIGHT = 600
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
        self.snake = Snake(20)
        self.food = Food()
        self.score = 0
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.snake.change_direction()

    def update(self):
        if not self.running:
            return

        self.snake.move()
        if self.snake.check_collision():
            return self.game_over()

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.randomize_position()
            self.score += 1

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
    def __init__(self, speed):
        self.body = [
            (BLOCK_SIZE * 5, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 4, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 3, BLOCK_SIZE * 5),
        ]
        self.direction = [BLOCK_SIZE, 0]
        self.speed = speed

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

    def change_direction(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.direction != [BLOCK_SIZE, 0]:
            self.direction = [-BLOCK_SIZE, 0]

        if keys[pygame.K_RIGHT] and self.direction != [-BLOCK_SIZE, 0]:
            self.direction = [BLOCK_SIZE, 0]

        if keys[pygame.K_UP] and self.direction != [0, BLOCK_SIZE]:
            self.direction = [0, -BLOCK_SIZE]

        if keys[pygame.K_DOWN] and self.direction != [0, -BLOCK_SIZE]:
            self.direction = [0, BLOCK_SIZE]


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
        game.clock.tick(20)

    pygame.quit()


if __name__ == "__main__":
    game = initialize_game()
    main_loop(game)
