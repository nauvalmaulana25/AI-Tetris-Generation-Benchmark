import sys
import random
import pygame

# ----------------------------
# Configuration
# ----------------------------
WIDTH, HEIGHT = 400, 600        # Window size
COLS, ROWS = 10, 20             # Tetris board size
CELL = 28                       # Cell size in pixels
BORDER = 12                     # Border/margin around playfield
FPS = 60

# Derived dimensions
PLAY_W = COLS * CELL
PLAY_H = ROWS * CELL

# Colors
BLACK = (12, 12, 16)
GRAY = (40, 40, 48)
LIGHT_GRAY = (70, 70, 80)
WHITE = (230, 230, 235)

# Tetromino colors (by piece type)
COLORS = {
    'I': (0, 180, 220),
    'O': (240, 210, 0),
    'T': (160, 70, 200),
    'S': (60, 200, 85),
    'Z': (230, 50, 60),
    'J': (65, 95, 220),
    'L': (245, 150, 45),
    None: (22, 22, 28)
}

# Scoring (classic-ish)
SCORES_PER_LINES = {1: 100, 2: 300, 3: 500, 4: 800}

# Controls:
# Left/Right: Move
# Down: Soft drop
# Space: Hard drop
# Up or X: Rotate CW
# Z: Rotate CCW (optional bonus)
# P: Pause
# R: Restart

# ----------------------------
# Tetromino definitions
# ----------------------------
# Each piece defined by a list of rotation states, each state a list of (x,y) blocks.
# Coordinates are relative to a 4x4 bounding box with origin at top-left.
# We'll use SRS-like spawn orientations and a simple rotation/wall-kick strategy.
PIECES = {
    'I': [
        [(0, 2), (1, 2), (2, 2), (3, 2)],  # ---- horizontal
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # | vertical
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(1, 0), (1, 1), (1, 2), (1, 3)]
    ],
    'O': [
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)]
    ],
    'T': [
        [(1, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (1, 3)],
        [(1, 1), (0, 2), (1, 2), (1, 3)]
    ],
    'S': [
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 1), (1, 2), (2, 2), (2, 3)],
        [(1, 2), (2, 2), (0, 3), (1, 3)],
        [(0, 1), (0, 2), (1, 2), (1, 3)]
    ],
    'Z': [
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 1), (1, 2), (2, 2), (1, 3)],
        [(0, 2), (1, 2), (1, 3), (2, 3)],
        [(1, 1), (0, 2), (1, 2), (0, 3)]
    ],
    'J': [
        [(0, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (2, 3)],
        [(1, 1), (1, 2), (0, 3), (1, 3)]
    ],
    'L': [
        [(2, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (1, 3), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (0, 3)],
        [(0, 1), (1, 1), (1, 2), (1, 3)]
    ]
}

# Spawn positions: pieces are placed into a 4x4 area whose top-left is at (3, -2) relative to board,
# letting parts start above the visible board like standard Tetris.
SPAWN_X, SPAWN_Y = 3, -2

# Simple wall-kick offsets to try after rotation (subset of SRS-inspired moves)
KICK_TESTS = [(0,0), (1,0), (-1,0), (0,-1), (2,0), (-2,0)]

# ----------------------------
# Helper functions
# ----------------------------
def create_grid():
    # 2D grid of None or piece letter
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def get_piece_shape(letter, rot):
    return PIECES[letter][rot % 4]

def piece_blocks(letter, rot, px, py):
    # Returns absolute board coordinates of blocks for piece at position (px, py)
    for (x, y) in get_piece_shape(letter, rot):
        yield (px + x, py + y)

def valid_position(grid, letter, rot, px, py):
    for x, y in piece_blocks(letter, rot, px, py):
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] is not None:
            return False
    return True

def lock_piece(grid, letter, rot, px, py):
    for x, y in piece_blocks(letter, rot, px, py):
        if 0 <= y < ROWS:
            grid[y][x] = letter

def clear_lines(grid):
    full_rows = [i for i, row in enumerate(grid) if all(cell is not None for cell in row)]
    if not full_rows:
        return 0
    for i in full_rows:
        del grid[i]
        grid.insert(0, [None for _ in range(COLS)])
    return len(full_rows)

def bag_generator():
    # 7-bag randomizer
    bag = []
    while True:
        if not bag:
            bag = list(PIECES.keys())
            random.shuffle(bag)
        yield bag.pop()

# ----------------------------
# Rendering
# ----------------------------
def draw_cell(surface, x, y, color, ghost=False):
    px = BORDER + x * CELL
    py = BORDER + y * CELL
    r = pygame.Rect(px, py, CELL, CELL)
    base = color
    if ghost:
        base = tuple(min(255, int(c * 0.45) + 40) for c in color)
    pygame.draw.rect(surface, base, r)
    # inner shading
    inner = r.inflate(-4, -4)
    pygame.draw.rect(surface, (255,255,255,35), inner, border_radius=4)
    # border
    pygame.draw.rect(surface, (0,0,0), r, 1)

def draw_grid(surface, grid):
    # background
    play_rect = pygame.Rect(BORDER, BORDER, PLAY_W, PLAY_H)
    pygame.draw.rect(surface, GRAY, play_rect, border_radius=8)
    for y in range(ROWS):
        for x in range(COLS):
            c = grid[y][x]
            color = COLORS[c] if c in COLORS else COLORS[None]
            if c is None:
                # subtle checker
                if (x + y) % 2 == 0:
                    color = (28, 28, 36)
                else:
                    color = (24, 24, 32)
            draw_cell(surface, x, y, color)

def draw_current(surface, letter, rot, px, py):
    for x, y in piece_blocks(letter, rot, px, py):
        if y >= 0:
            draw_cell(surface, x, y, COLORS[letter])

def compute_ghost_y(grid, letter, rot, px, py):
    gy = py
    while valid_position(grid, letter, rot, px, gy + 1):
        gy += 1
    return gy

def draw_ghost(surface, grid, letter, rot, px, py):
    gy = compute_ghost_y(grid, letter, rot, px, py)
    for x, y in piece_blocks(letter, rot, px, gy):
        if y >= 0:
            draw_cell(surface, x, y, COLORS[letter], ghost=True)

def draw_hud(surface, score, level, lines, next_piece, held_piece, paused, game_over):
    font = pygame.font.SysFont("consolas", 20)
    big = pygame.font.SysFont("consolas", 32, bold=True)

    # Right panel
    panel_x = BORDER + PLAY_W + 12
    # Title
    title = big.render("TETRIS", True, WHITE)
    surface.blit(title, (panel_x, BORDER))

    # Score/Level/Lines
    y = BORDER + 50
    for label, value in [("SCORE", score), ("LEVEL", level), ("LINES", lines)]:
        txt = font.render(f"{label}: {value}", True, WHITE)
        surface.blit(txt, (panel_x, y))
        y += 24

    # Next piece preview
    y += 10
    surface.blit(font.render("NEXT", True, WHITE), (panel_x, y))
    y += 8
    draw_preview(surface, next_piece, panel_x, y)
    y += 110

    # Hold (not used here for gameplay fairness; we can display None)
    surface.blit(font.render("HOLD", True, WHITE), (panel_x, y))
    y += 8
    draw_preview(surface, held_piece, panel_x, y)

    # Pause / Game over overlays
    if paused:
        overlay = big.render("PAUSED", True, WHITE)
        surface.blit(overlay, (BORDER + 20, HEIGHT // 2 - 20))
    if game_over:
        overlay = big.render("GAME OVER", True, WHITE)
        surface.blit(overlay, (BORDER + 10, HEIGHT // 2 - 20))
        surface.blit(font.render("Press R to restart", True, WHITE), (BORDER + 14, HEIGHT // 2 + 16))

def draw_preview(surface, letter, ox, oy):
    box = pygame.Rect(ox, oy, 120, 100)
    pygame.draw.rect(surface, LIGHT_GRAY, box, border_radius=8)
    pygame.draw.rect(surface, (0,0,0), box, 1)
    if not letter:
        return
    # Center the piece roughly inside the preview box
    # Render using the 0 rotation
    shape = get_piece_shape(letter, 0)
    xs = [x for x, _ in shape]
    ys = [y for _, y in shape]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = (maxx - minx + 1) * CELL * 0.7
    h = (maxy - miny + 1) * CELL * 0.7
    start_x = ox + (box.width - w) / 2
    start_y = oy + (box.height - h) / 2
    scale = 0.7
    for x, y in shape:
        rx = start_x + (x - minx) * CELL * scale
        ry = start_y + (y - miny) * CELL * scale
        r = pygame.Rect(rx, ry, CELL * scale, CELL * scale)
        pygame.draw.rect(surface, COLORS[letter], r)
        pygame.draw.rect(surface, (0,0,0), r, 1)

# ----------------------------
# Game class
# ----------------------------
class Tetris:
    def __init__(self):
        self.grid = create_grid()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_interval = 0.9  # seconds per soft drop tick initially
        self.drop_timer = 0.0

        self.piece_gen = bag_generator()
        self.current = None
        self.spawn_new_piece()

        self.next_piece = next(self.piece_gen)
        self.held_piece = None  # not used; display only
        self.paused = False
        self.game_over = False

        # Input buffering for DAS-like feel
        self.move_dir = 0
        self.move_repeat_delay = 0.13
        self.move_repeat_rate = 0.04
        self.move_timer = 0.0
        self.move_initial_delay_done = False

        self.soft_drop = False

    def spawn_new_piece(self):
        if self.current is None:
            letter = next(self.piece_gen)
        else:
            letter = self.next_piece
        self.current = {
            'letter': letter,
            'rot': 0,
            'x': SPAWN_X,
            'y': SPAWN_Y
        }
        # Preload next
        self.next_piece = next(self.piece_gen)
        # If spawn invalid, game over
        if not valid_position(self.grid, self.current['letter'], self.current['rot'], self.current['x'], self.current['y']):
            self.game_over = True

    def rotate(self, cw=True):
        if self.game_over or self.paused:
            return
        letter = self.current['letter']
        rot = self.current['rot']
        px, py = self.current['x'], self.current['y']
        new_rot = (rot + (1 if cw else -1)) % 4
        # Try wall-kicks
        for dx, dy in KICK_TESTS:
            if valid_position(self.grid, letter, new_rot, px + dx, py + dy):
                self.current['rot'] = new_rot
                self.current['x'] = px + dx
                self.current['y'] = py + dy
                return
        # If none valid, no rotation

    def move(self, dx):
        if self.game_over or self.paused:
            return
        px, py = self.current['x'], self.current['y']
        if valid_position(self.grid, self.current['letter'], self.current['rot'], px + dx, py):
            self.current['x'] += dx

    def drop_one(self):
        # Attempts to move down by 1; returns True if moved, False if locked
        px, py = self.current['x'], self.current['y']
        if valid_position(self.grid, self.current['letter'], self.current['rot'], px, py + 1):
            self.current['y'] += 1
            return True
        else:
            # Lock piece
            lock_piece(self.grid, self.current['letter'], self.current['rot'], px, py)
            # Clear lines
            cleared = clear_lines(self.grid)
            if cleared > 0:
                self.lines += cleared
                self.score += SCORES_PER_LINES.get(cleared, 0) * self.level
                # Increase level every 10 lines
                new_level = 1 + self.lines // 10
                if new_level > self.level:
                    self.level = new_level
                    # Increase speed
                    self.drop_interval = max(0.12, 0.9 - (self.level - 1) * 0.08)
            # Spawn next
            self.spawn_new_piece()
            return False

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        gy = compute_ghost_y(self.grid, self.current['letter'], self.current['rot'], self.current['x'], self.current['y'])
        dist = max(0, gy - self.current['y'])
        # Per-cell hard drop points (optional): add small reward
        self.score += dist * 2
        self.current['y'] = gy
        # Lock immediately
        self.drop_one()

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused

    def restart(self):
        self.__init__()

    def update(self, dt):
        if self.game_over or self.paused:
            return
        # Gravity
        interval = self.drop_interval
        if self.soft_drop:
            interval = min(0.03, self.drop_interval * 0.25)
        self.drop_timer += dt
        while self.drop_timer >= interval:
            moved = self.drop_one()
            self.drop_timer -= interval
            if not moved:
                break

        # Lateral movement repeat
        if self.move_dir != 0:
            self.move_timer += dt
            if not self.move_initial_delay_done:
                if self.move_timer >= self.move_repeat_delay:
                    self.move(px_dir=self.move_dir)
                    self.move_timer -= self.move_repeat_delay
                    self.move_initial_delay_done = True
            else:
                while self.move_timer >= self.move_repeat_rate:
                    self.move(px_dir=self.move_dir)
                    self.move_timer -= self.move_repeat_rate

    def move(self, px_dir):
        self.move_piece(px_dir)

    def move_piece(self, dx):
        # helper separated to match two call styles
        self.move(dx)

# ----------------------------
# Main loop
# ----------------------------
def main():
    pygame.init()
    # Adjust window width to include side panel
    panel_w = 150
    window = pygame.display.set_mode((BORDER + PLAY_W + panel_w, BORDER + PLAY_H))
    pygame.display.set_caption("Tetris - pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    game = Tetris()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    running = False
                elif event.key == pygame.K_p:
                    game.toggle_pause()
                elif event.key == pygame.K_r:
                    game.restart()
                if game.game_over:
                    continue
                if event.key == pygame.K_LEFT:
                    game.move_dir = -1
                    game.move_initial_delay_done = False
                    game.move_timer = 0.0
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move_dir = 1
                    game.move_initial_delay_done = False
                    game.move_timer = 0.0
                    game.move(1)
                elif event.key == pygame.K_DOWN:
                    game.soft_drop = True
                elif event.key in (pygame.K_UP, pygame.K_x):
                    game.rotate(cw=True)
                elif event.key == pygame.K_z:
                    game.rotate(cw=False)
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if (event.key == pygame.K_LEFT and game.move_dir == -1) or (event.key == pygame.K_RIGHT and game.move_dir == 1):
                        game.move_dir = 0
                        game.move_timer = 0.0
                        game.move_initial_delay_done = False
                elif event.key == pygame.K_DOWN:
                    game.soft_drop = False

        # Update
        game.update(dt)

        # Render
        window.fill(BLACK)
        draw_grid(window, game.grid)
        if not game.game_over:
            draw_ghost(window, game.grid, game.current['letter'], game.current['rot'], game.current['x'], game.current['y'])
            draw_current(window, game.current['letter'], game.current['rot'], game.current['x'], game.current['y'])
        else:
            # Show final position locked already by game-over detection (no current piece)
            pass

        # HUD
        draw_hud(window, game.score, game.level, game.lines, game.next_piece, game.held_piece, game.paused, game.game_over)

        # Controls hint
        hint = font.render("Arrows: Move/Soft Drop | Up/X: Rotate | Space: Hard Drop | P: Pause | R: Restart", True, WHITE)
        window.blit(hint, (BORDER, HEIGHT - 24))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()