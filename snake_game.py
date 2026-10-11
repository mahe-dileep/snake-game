"""Minimal Snake; pygame is the only third-party dependency."""
from random import randrange
import pygame

GRID_WIDTH = GRID_HEIGHT = 30
CELL_SIZE, FPS, HUD_HEIGHT = 25, 10, 30
BACKGROUND, GRID_COLOR = (20, 24, 28), (40, 46, 52)
HEAD_COLOR, BODY_COLOR = (130, 240, 120), (50, 170, 80)
FOOD_COLOR, TEXT_COLOR = (240, 80, 80), (240, 240, 240)
# Clockwise: right, down, left, up. In pygame, y increases downward.
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
class SnakeGame:
    def __init__(self, render=True):
        self.render_enabled = render  # Keep the render() method callable.
        self.grid_width, self.grid_height = GRID_WIDTH, GRID_HEIGHT
        self.cell_size, self.fps = CELL_SIZE, FPS
        self.screen = self.font = self.clock = None
        if render:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE + HUD_HEIGHT))
            pygame.display.set_caption("Snake")
            self.font = pygame.font.Font(None, 24)
            self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        """Start centered, length three, facing right; return the state."""
        x, y = self.grid_width // 2, self.grid_height // 2
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = self.score = self.steps_since_food = 0
        self._place_food()
        return self.get_state()

    def _place_food(self):
        """Retry random cells until free; None means the board is full."""
        self.food = None
        if len(self.snake) == self.grid_width * self.grid_height:
            return
        while self.food is None or self.food in self.snake:
            self.food = (randrange(self.grid_width), randrange(self.grid_height))

    def step(self, action):
        """Apply 0=straight, 1=right, 2=left; return state, reward, done, score."""
        if action not in (0, 1, 2):
            raise ValueError("action must be 0, 1, or 2")
        self.direction = (self.direction + (0, 1, -1)[action]) % 4
        dx, dy = DIRECTIONS[self.direction]
        x, y = self.snake[0][0] + dx, self.snake[0][1] + dy
        self.steps_since_food += 1
        if (not (0 <= x < self.grid_width and 0 <= y < self.grid_height)
                or (x, y) in self.snake
                or self.steps_since_food > 100 * len(self.snake)):
            return self.get_state(), -10, True, self.score
        self.snake.insert(0, (x, y))
        reward = 0
        if (x, y) == self.food:
            self.score += 1
            self.steps_since_food, reward = 0, 10
            self._place_food()
        else:
            self.snake.pop()
        # Filling the board ends the game without an endless food search.
        return self.get_state(), reward, self.food is None, self.score

    def get_state(self):
        """Return danger S/R/L, direction L/R/U/D, food L/R/U/D as 11 bits."""
        x, y = self.snake[0]
        danger = []
        for turn in (0, 1, -1):
            dx, dy = DIRECTIONS[(self.direction + turn) % 4]
            nx, ny = x + dx, y + dy
            danger.append(not (0 <= nx < self.grid_width and 0 <= ny < self.grid_height)
                          or (nx, ny) in self.snake)
        moving = [self.direction == d for d in (2, 0, 3, 1)]
        fx, fy = self.food if self.food is not None else (x, y)
        return tuple(int(v) for v in danger + moving + [fx < x, fx > x, fy < y, fy > y])

    def render(self):
        """Draw the grid, snake, food, and score; headless mode does nothing."""
        if not self.render_enabled:
            return
        self.screen.fill(BACKGROUND)
        width, height = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
        for x in range(0, width + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, HUD_HEIGHT), (x, HUD_HEIGHT + height))
        for y in range(0, height + 1, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y + HUD_HEIGHT), (width, y + HUD_HEIGHT))
        cells = [(cell, HEAD_COLOR if i == 0 else BODY_COLOR) for i, cell in enumerate(self.snake)]
        for (x, y), color in cells + ([(self.food, FOOD_COLOR)] if self.food is not None else []):
            pygame.draw.rect(self.screen, color, (x * CELL_SIZE + 1,
                             y * CELL_SIZE + HUD_HEIGHT + 1, CELL_SIZE - 2, CELL_SIZE - 2))
        self.screen.blit(self.font.render(f"Score: {self.score}", True, TEXT_COLOR), (8, 5))
        pygame.display.flip()

def play_human():
    """Use arrow keys; opposite-direction requests are ignored."""
    game = SnakeGame(render=True)
    keys = {pygame.K_RIGHT: 0, pygame.K_DOWN: 1, pygame.K_LEFT: 2, pygame.K_UP: 3}
    running = True
    while running:
        action = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in keys:
                turn = (keys[event.key] - game.direction) % 4
                if turn != 2:  # Do not reverse into the snake's own body.
                    action = {0: 0, 1: 1, 3: 2}[turn]
        if not running:
            break
        _, _, done, _ = game.step(action)
        game.render()
        if done:
            game.reset()
        game.clock.tick(game.fps)  # Only human play is speed-limited.
    pygame.quit()
if __name__ == "__main__":
    play_human()
