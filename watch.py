import pickle
from collections import defaultdict

import pygame

import snake_game


def new_row():
    return [0, 0, 0]  # straight, right, left


# Load the trained table (new, unseen situations start at [0, 0, 0])
with open("qtable.pkl", "rb") as f:
    table = defaultdict(new_row, pickle.load(f))


def best_move(state):
    row = table[state]
    return row.index(max(row))  # always play its best move (no exploring)


game = snake_game.SnakeGame(render=True)
clock = pygame.time.Clock()
speed = 15  # moves per second: lower = slower, higher = faster

for game_number in range(1, 6):  # watch 5 games
    state = game.reset()
    done = False
    while not done:
        for event in pygame.event.get():  # keeps the window responsive
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        state, reward, done, score = game.step(best_move(state))
        game.render()
        clock.tick(speed)
    print(f"Game {game_number}: score {score}")
    pygame.time.wait(1000)  # 1-second pause between games

pygame.quit()
