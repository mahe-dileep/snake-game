import random
import pickle
from collections import defaultdict

import snake_game

# --- Settings ---
learning_rate = 0.1
discount = 0.9
epsilon_start = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
games = 5000
random_seed = 0


def new_row():
    return [0, 0, 0]  # values for: straight, right, left


table = defaultdict(new_row)


def choose_move(state, epsilon):
    num = random.random()
    if num < epsilon:
        return random.randint(0, 2)        # explore: random move
    else:
        row = table[state]
        maximum = max(row)
        best_move = row.index(maximum)     # exploit: best-known move
        return best_move


def update(state, action, reward, next_state, done):
    current_value = table[state][action]
    if done:
        target = reward                    # no future after death
    else:
        target = reward + discount * max(table[next_state])
    new_value = current_value + learning_rate * (target - current_value)
    table[state][action] = new_value


def evaluate(n_games, epsilon):
    """Play n_games WITHOUT learning and return the average score."""
    total = 0
    for _ in range(n_games):
        state = game.reset()
        done = False
        while not done:
            move = choose_move(state, epsilon)
            state, reward, done, score = game.step(move)
        total += score
    return total / n_games


# --- Setup ---
random.seed(random_seed)                    # reproducible runs
game = snake_game.SnakeGame(render=False)   # no window, so it trains fast
epsilon = epsilon_start                     # start fully random
scores = []                                 # one score per training game

# --- Baseline: a purely random snake ---
random_avg = evaluate(100, epsilon=1.0)
print(f"Random snake average (100 games): {random_avg:.2f}")

# --- Training ---
for episode in range(games):
    state = game.reset()
    done = False
    while not done:
        move = choose_move(state, epsilon)
        next_state, reward, done, score = game.step(move)
        update(state, move, reward, next_state, done)
        state = next_state
    scores.append(score)
    epsilon = max(epsilon_min, epsilon * epsilon_decay)
    if (episode + 1) % 50 == 0:
        avg = sum(scores[-50:]) / len(scores[-50:])
        print(f"Game {episode + 1} | avg (last 50): {avg:.2f} | epsilon: {epsilon:.3f}")

# --- Fair test: exploring off, no learning ---
trained_avg = evaluate(20, epsilon=0.0)
print(f"Trained snake average (20 games): {trained_avg:.2f}  vs  random: {random_avg:.2f}")

# --- Save for the video and later ---
with open("qtable.pkl", "wb") as f:
    pickle.dump(dict(table), f)
with open("scores.pkl", "wb") as f:
    pickle.dump(scores, f)
print("Saved qtable.pkl and scores.pkl")
