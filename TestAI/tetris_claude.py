import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}


class Tetromino:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.shape = [row[:] for row in SHAPES[shape_name]]
        self.color = SHAPE_COLORS[shape_name]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """Rotate the shape 90 degrees clockwise"""
        rotated = [[self.shape[len(self.shape) - 1 - j][i] 
                   for j in range(len(self.shape))] 
                  for i in range(len(self.shape[0]))]
        return rotated


class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + SIDEBAR_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def new_piece(self):
        """Create a new random tetromino"""
        shape_name = random.choice(list(SHAPES.keys()))
        return Tetromino(shape_name)

    def valid_move(self, piece, x, y, shape=None):
        """Check if a move is valid"""
        if shape is None:
            shape = piece.shape
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    
                    # Check boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    
                    # Check collision with settled blocks
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        
        return True

    def merge_piece(self):
        """Merge current piece into the grid"""
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + i
                    grid_x = self.current_piece.x + j
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = 1
                        self.grid_colors[grid_y][grid_x] = self.current_piece.color

    def clear_lines(self):
        """Clear completed lines and update score"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                del self.grid_colors[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                self.grid_colors.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        
        # Scoring system
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        elif lines_cleared == 4:
            self.score += 800

    def move_down(self):
        """Move piece down one row"""
        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
            return True
        else:
            self.merge_piece()
            self.clear_lines()
            self.current_piece = self.new_piece()
            
            # Check game over
            if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                self.game_over = True
            
            return False

    def move_left(self):
        """Move piece left"""
        if self.valid_move(self.current_piece, self.current_piece.x - 1, self.current_piece.y):
            self.current_piece.x -= 1

    def move_right(self):
        """Move piece right"""
        if self.valid_move(self.current_piece, self.current_piece.x + 1, self.current_piece.y):
            self.current_piece.x += 1

    def rotate_piece(self):
        """Rotate piece 90 degrees clockwise"""
        rotated_shape = self.current_piece.rotate()
        
        if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, rotated_shape):
            self.current_piece.shape = rotated_shape

    def hard_drop(self):
        """Drop piece to the bottom instantly"""
        while self.move_down():
            self.score += 2

    def draw_grid(self):
        """Draw the game grid"""
        # Draw settled blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid_colors[y][x], rect)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)
                else:
                    pygame.draw.rect(self.screen, BLACK, rect)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Draw current piece
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = (self.current_piece.x + j) * GRID_SIZE
                    y = (self.current_piece.y + i) * GRID_SIZE
                    if y >= 0:
                        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                        pygame.draw.rect(self.screen, self.current_piece.color, rect)
                        pygame.draw.rect(self.screen, GRAY, rect, 1)

    def draw_sidebar(self):
        """Draw the sidebar with score and instructions"""
        sidebar_x = GRID_WIDTH * GRID_SIZE
        
        # Draw background
        pygame.draw.rect(self.screen, BLACK, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        # Draw score
        score_text = self.font.render("SCORE", True, WHITE)
        self.screen.blit(score_text, (sidebar_x + 20, 50))
        
        score_value = self.font.render(str(self.score), True, WHITE)
        self.screen.blit(score_value, (sidebar_x + 20, 90))
        
        # Draw instructions
        instructions = [
            "CONTROLS:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "SPACE : Hard Drop"
        ]
        
        y_offset = 200
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (sidebar_x + 10, y_offset + i * 30))

    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_sidebar()
        
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def reset(self):
        """Reset the game"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.fall_time = 0

    def run(self):
        """Main game loop"""
        while True:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset()
                    else:
                        if event.key == pygame.K_LEFT:
                            self.move_left()
                        elif event.key == pygame.K_RIGHT:
                            self.move_right()
                        elif event.key == pygame.K_DOWN:
                            self.move_down()
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
            
            # Auto fall
            if not self.game_over:
                if current_time - self.fall_time > self.fall_speed:
                    self.move_down()
                    self.fall_time = current_time
            
            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Tetris()
    game.run()