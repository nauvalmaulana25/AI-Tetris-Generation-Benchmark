import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1], [1, 1]],      # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Tetromino colors
SHAPE_COLORS = [CYAN, PURPLE, ORANGE, BLUE, YELLOW, GREEN, RED]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.score = 0
        self.game_over = False

    def new_piece(self):
        self.current_piece = Tetromino(self.width // 2 - 1, 0, random.choice(SHAPES))

    def check_collision(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if (piece.y + y >= self.height or
                            piece.x + x < 0 or
                            piece.x + x >= self.width or
                            self.grid[piece.y + y][piece.x + x]):
                        return True
        return False

    def lock_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece.y + y][piece.x + x] = piece.color
        self.clear_lines()

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [0 for _ in range(self.width)])
        self.score += len(lines_to_clear) * 100

    def update(self):
        if not self.current_piece:
            self.new_piece()
            if self.check_collision(self.current_piece):
                self.game_over = True

        if not self.game_over:
            self.current_piece.y += 1
            if self.check_collision(self.current_piece):
                self.current_piece.y -= 1
                self.lock_piece(self.current_piece)
                self.new_piece()
                if self.check_collision(self.current_piece):
                    self.game_over = True

    def move(self, dx):
        self.current_piece.x += dx
        if self.check_collision(self.current_piece):
            self.current_piece.x -= dx

    def rotate(self):
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()


def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x]:
                pygame.draw.rect(surface, grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

def draw_piece(surface, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, piece.color, ((piece.x + x) * GRID_SIZE, (piece.y + y) * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

def draw_score(surface, score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (10, 10))

def draw_game_over(surface):
    font = pygame.font.Font(None, 48)
    text = font.render("Game Over", True, RED)
    surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris(BOARD_WIDTH, BOARD_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and not game.game_over:
                if event.key == pygame.K_LEFT:
                    game.move(-1)
                if event.key == pygame.K_RIGHT:
                    game.move(1)
                if event.key == pygame.K_DOWN:
                    game.update()
                if event.key == pygame.K_UP:
                    game.rotate()

        screen.fill(BLACK)

        if not game.game_over:
            game.update()

        draw_grid(screen, game.grid)
        if game.current_piece:
            draw_piece(screen, game.current_piece)
        draw_score(screen, game.score)

        if game.game_over:
            draw_game_over(screen)

        pygame.display.flip()
        clock.tick(5)

    pygame.quit()


if __name__ == "__main__":
    main()