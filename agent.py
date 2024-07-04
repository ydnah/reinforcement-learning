import random
from collections import deque

import numpy as np
import pygame
import torch

from gameAI import Game
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        # Get the state of the snake
        return game.get_snake_state()

    def remeber(self, state, action, reward, next_state, done):
        # Store to memory
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        # Check there is more then items in memory then the batch size
        if len(self.memory) > BATCH_SIZE:
            # Take a random sample
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            # Take whole of memory if not
            mini_sample = self.memory

        # Pairs elements of the mini sample together
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        # Complete a step
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Determine if a move is going to be random for from prediciton (traderoff exploration/exploitations)
        self.epsilon = 80 - self.n_games
        # Create move
        final_move = [0, 0, 0]
        # Get a random int, if its less then epsilion make the snake move randomly
        if random.randint(0, 200) < self.epsilon:
            # Get a random int
            move = random.randint(0, 2)
            # Turn a value from move to true, indiciting snakes next move
            final_move[move] = 1
        # If not a random move
        else:
            # Convert state to tensor
            state0 = torch.tensor(state, dtype=torch.float)
            # Get next move
            prediction = self.model(state0)
            # Returns [0, 0, 0] get the highest value and a item of the list
            move = torch.argmax(prediction).item()
            # Set direction to move
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    pygame.init()
    agent = Agent()
    game = Game()
    while True:
        game.handle_events()
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.update(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remeber(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f"Game= {agent.n_games}, Score= {score}, Record= {record}")

        game.render()
        game.clock.tick(100)


if __name__ == "__main__":
    train()
