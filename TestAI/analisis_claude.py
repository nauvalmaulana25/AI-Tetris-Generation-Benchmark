import unittest
import pygame
import sys


try:
    from tetris_claude import Tetris, Tetromino, SHAPES, GRID_WIDTH, GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
except ImportError:
    print("Error: File 'tetris_claude.py' tidak ditemukan.")
    print("Pastikan nama file kode game adalah 'tetris_claude.py'.")
    sys.exit(1)

def calculate_metrics(filename):
    print(f"\n[{filename}] ANALISIS METRIK KODE (CLAUDE 4.5 SONNET):")
    try:

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan.")
        return

    total_lines = len(lines)
    empty_lines = 0
    comment_lines = 0
    functional_lines = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            empty_lines += 1
        elif stripped.startswith('#'):
            comment_lines += 1
        else:
            functional_lines += 1

    lpe = (functional_lines / total_lines) * 100 if total_lines > 0 else 0
    
    print(f"  - Total Lines of Code (LOC) : {total_lines}")
    print(f"  - Functional Lines          : {functional_lines}")
    print(f"  - Empty/Comment Lines       : {empty_lines + comment_lines}")
    print(f"  - Line Processing Efficiency: {lpe:.2f}%")
    print("-" * 40)


class TestTetrisClaude(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pygame.init()

        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def setUp(self):

        self.game = Tetris()


    def test_t1_board_initialization(self):
        self.assertEqual(len(self.game.grid), GRID_HEIGHT)
        self.assertEqual(len(self.game.grid[0]), GRID_WIDTH)

        self.assertTrue(all(c == 0 for row in self.game.grid for c in row))


    def test_t2_block_spawning(self):
        self.game.current_piece = self.game.new_piece()
        self.assertIsNotNone(self.game.current_piece)

        self.assertEqual(self.game.current_piece.y, 0)
        self.assertTrue(0 <= self.game.current_piece.x < GRID_WIDTH)


    def test_t3_horizontal_movement(self):
        initial_x = self.game.current_piece.x
        

        self.game.move_left()
        new_x = self.game.current_piece.x

        self.assertTrue(new_x == initial_x - 1)
        

        self.game.move_right()
        self.assertEqual(self.game.current_piece.x, initial_x)


    def test_t4_simple_rotation(self):

        self.game.current_piece = Tetromino('T')
        shape_before = [row[:] for row in self.game.current_piece.shape]
        
        self.game.rotate_piece()
        
        shape_after = self.game.current_piece.shape
        self.assertNotEqual(shape_before, shape_after)


    def test_t5_bottom_collision(self):

        self.game.current_piece = Tetromino('I') 

        self.game.current_piece.y = GRID_HEIGHT - 1
        

        result = self.game.move_down()
        

        self.assertFalse(result)
        

        row_filled = any(self.game.grid[GRID_HEIGHT-1])
        self.assertTrue(row_filled, "Grid paling bawah harus terisi setelah collision")


    def test_t6_lateral_collision(self):
        self.game.current_piece.x = 0 
        self.game.move_left() 
        self.assertEqual(self.game.current_piece.x, 0, "Piece tidak boleh tembus dinding kiri")


    def test_t7_wall_kick_rotation(self):

        self.game.current_piece = Tetromino('I')

        self.game.current_piece.shape = [[1], [1], [1], [1]] 
        

        self.game.current_piece.x = GRID_WIDTH - 1
        self.game.current_piece.y = 5
        

        shape_before = self.game.current_piece.shape
        self.game.rotate_piece()
        shape_after = self.game.current_piece.shape
        

        self.assertEqual(shape_before, shape_after, "Rotation should be cancelled near wall")
        self.assertTrue(self.game.current_piece.x < GRID_WIDTH)


    def test_t8_line_clearing(self):

        self.game.grid[GRID_HEIGHT-1] = [1] * GRID_WIDTH
        score_before = self.game.score
        
        self.game.clear_lines()
        

        self.assertEqual(self.game.score, score_before + 100)
        

        self.assertEqual(self.game.grid[GRID_HEIGHT-1], [0] * GRID_WIDTH)


    def test_t9_scoring_system(self):
        self.game.score = 0

        self.game.grid[GRID_HEIGHT-1] = [1] * GRID_WIDTH
        self.game.grid[GRID_HEIGHT-2] = [1] * GRID_WIDTH
        
        self.game.clear_lines()
        
        self.assertEqual(self.game.score, 300)


    def test_t10_game_over(self):

        self.game.grid[0] = [1] * GRID_WIDTH
        self.game.grid[1] = [1] * GRID_WIDTH
        

        self.game.current_piece = self.game.new_piece()
        

        is_valid = self.game.valid_move(self.game.current_piece, self.game.current_piece.x, self.game.current_piece.y)
        
        if not is_valid:
            self.game.game_over = True
            
        self.assertTrue(self.game.game_over, "Game Over harus True jika spawn area penuh")

if __name__ == '__main__':

    calculate_metrics('tetris_claude.py')
    

    print("\n[UNIT TEST EXECUTION - CLAUDE 4.5 SONNET]")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTetrisClaude)
    unittest.TextTestRunner(verbosity=2).run(suite)