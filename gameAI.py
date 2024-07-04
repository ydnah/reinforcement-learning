import random

import numpy as np
import pygame

# Global Variables
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
        # Resets game state variables
        self.snake = Snake()
        self.score = 0
        self.food.randomize_position()
        self.frame_iteration = 0
        self.running = True

    def handle_events(self):
        # Checks for game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, action):
        if not self.running:
            return

        self.frame_iteration += 1

        # Get action, move snake
        self.snake.change_direction(action)
        self.snake.move()

        # Implement rewards for the snake agent
        self.reward = 0

        # Check for collision
        # If snake hasnt increased in size for 100 * len(snake) punish snake
        if self.snake.check_collision(
            self.snake.body[0]
        ) or self.frame_iteration > 100 * len(self.snake.body):
            self.reward = -10
            self.running = False

            return self.reward, not self.running, self.score

        # If snake intercepts with food
        if self.snake.body[0] == self.food.position:
            # Grow snake, generate new food
            self.snake.grow()
            self.food.randomize_position()
            # Increase score, reward snake agent
            self.score += 1
            self.reward = 10

        return self.reward, not self.running, self.score

    # Render game
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

    def get_snake_state(self):
        # Get position of snake head
        head = self.snake.body[0]

        # Gets points around the head
        point_l = (head[0] - BLOCK_SIZE, head[1])
        point_r = (head[0] + BLOCK_SIZE, head[1])
        point_u = (head[0], head[1] - BLOCK_SIZE)
        point_d = (head[0], head[1] + BLOCK_SIZE)

        # Gets the direction of the snake
        dir_l = self.snake.direction == [-BLOCK_SIZE, 0]
        dir_r = self.snake.direction == [BLOCK_SIZE, 0]
        dir_u = self.snake.direction == [0, -BLOCK_SIZE]
        dir_d = self.snake.direction == [0, BLOCK_SIZE]

        # Returns the current stake the snake
        state = [
            # Direction of danger [0, 0, 0, ....]
            # Danger forward
            (dir_r and self.snake.check_collision(point_r))
            or (dir_l and self.snake.check_collision(point_l))
            or (dir_u and self.snake.check_collision(point_u))
            or (dir_d and self.snake.check_collision(point_d)),
            # Danger right
            (dir_u and self.snake.check_collision(point_r))
            or (dir_d and self.snake.check_collision(point_l))
            or (dir_l and self.snake.check_collision(point_u))
            or (dir_r and self.snake.check_collision(point_d)),
            # Danger left
            (dir_d and self.snake.check_collision(point_r))
            or (dir_u and self.snake.check_collision(point_l))
            or (dir_r and self.snake.check_collision(point_u))
            or (dir_l and self.snake.check_collision(point_d)),
            # Direction snake is moving [... 0, 0, 0, 0, ....]
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            # Position of food relaive the snake head [... 0, 0, 0, 0]
            self.food.position[0] < head[0],
            self.food.position[0] > head[0],
            self.food.position[1] < head[1],
            self.food.position[1] > head[1],
        ]

        return np.array(state, dtype=int)


class Snake:
    def __init__(self):
        # Initialize snake to 3 blocks long
        self.body = [
            (BLOCK_SIZE * 5, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 4, BLOCK_SIZE * 5),
            (BLOCK_SIZE * 3, BLOCK_SIZE * 5),
        ]
        # Set original snake direction to right
        self.direction = [BLOCK_SIZE, 0]

    def move(self):
        # Gets the first element in the list
        head_x, head_y = self.body[0]

        # Creates new head
        new_head = (
            head_x + self.direction[0],
            head_y + self.direction[1],
        )
        self.body = [new_head] + self.body[:-1]

    def grow(self):
        # Add block to end of snake
        self.body.append(self.body[-1])

    def check_collision(self, pt):
        if pt is None:
            pt = self.body[0]
        # Checks for collision with game axis
        if pt[0] < 0 or pt[0] >= WIDTH or pt[1] < 0 or pt[1] >= HEIGHT:
            return True
        # Checks for collision with body
        if pt in self.body[1:]:
            return True
        return False

    def change_direction(self, action=None):
        # [straight, right, left]

        if action is None:
            return

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
        # Randomly place food
        self.position = self.randomize_position()

    def randomize_position(self):
        # Generate random x, y for foood
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        # Set position of food
        self.position = (x, y)
        return self.position
