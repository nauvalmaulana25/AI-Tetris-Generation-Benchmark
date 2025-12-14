import unittest
import pygame
import sys


try:
    from tetris_gemini import Tetris, Tetromino, SHAPES, BOARD_WIDTH, BOARD_HEIGHT
except ImportError:
    print("Error: File 'tetris_gemini.py' tidak ditemukan.")
    sys.exit(1)


def calculate_metrics(filename):
    print(f"\n[{filename}] ANALISIS METRIK KODE:")
    try:
        with open(filename, 'r') as f:
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


class TestTetrisGemini(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def setUp(self):
        self.game = Tetris(BOARD_WIDTH, BOARD_HEIGHT)


    def test_t1_board_initialization(self):
        self.assertEqual(len(self.game.grid), BOARD_HEIGHT)
        self.assertEqual(len(self.game.grid[0]), BOARD_WIDTH)
        self.assertTrue(all(c == 0 for row in self.game.grid for c in row))


    def test_t2_block_spawning(self):
        self.game.new_piece()
        self.assertIsNotNone(self.game.current_piece)
        self.assertEqual(self.game.current_piece.y, 0)
        self.assertTrue(0 <= self.game.current_piece.x < BOARD_WIDTH)


    def test_t3_horizontal_movement(self):
        self.game.new_piece()
        initial_x = self.game.current_piece.x
        self.game.move(-1)
        self.assertEqual(self.game.current_piece.x, initial_x - 1)
        self.game.move(1)
        self.assertEqual(self.game.current_piece.x, initial_x)


    def test_t4_simple_rotation(self):
        self.game.current_piece = Tetromino(5, 5, [[1, 1, 1], [0, 1, 0]])
        shape_before = self.game.current_piece.shape
        self.game.rotate()
        shape_after = self.game.current_piece.shape
        self.assertNotEqual(shape_before, shape_after)


    def test_t5_bottom_collision(self):
        self.game.new_piece()
        

        self.game.current_piece.shape = [[1, 1, 1, 1]]
        

        self.game.current_piece.y = BOARD_HEIGHT - 1
        

        self.game.update()
        

        row_filled = any(self.game.grid[BOARD_HEIGHT-1])
        self.assertTrue(row_filled, "Grid paling bawah harus terisi setelah collision")


    def test_t6_lateral_collision(self):
        self.game.new_piece()
        self.game.current_piece.x = 0 
        self.game.move(-1)
        self.assertEqual(self.game.current_piece.x, 0)


    def test_t7_wall_kick_rotation(self):
        self.game.new_piece()
        self.game.current_piece.shape = [[1, 1, 1, 1]] 
        self.game.current_piece.x = BOARD_WIDTH - 1
        self.game.current_piece.y = 5
        self.game.rotate()
        self.assertTrue(self.game.current_piece.x < BOARD_WIDTH)


    def test_t8_line_clearing(self):
        self.game.grid[BOARD_HEIGHT-1] = [1] * BOARD_WIDTH
        score_before = self.game.score
        self.game.clear_lines()
        self.assertGreater(self.game.score, score_before)
        self.assertEqual(self.game.grid[BOARD_HEIGHT-1], [0] * BOARD_WIDTH)


    def test_t9_scoring_system(self):
        self.game.score = 0
        self.game.grid[BOARD_HEIGHT-1] = [(255,0,0)] * BOARD_WIDTH
        self.game.clear_lines()
        self.assertEqual(self.game.score, 100)


    def test_t10_game_over(self):

        self.game.current_piece = None
        

        self.game.grid[0] = [1] * BOARD_WIDTH
        self.game.grid[1] = [1] * BOARD_WIDTH
        

        self.game.update()
        
        self.assertTrue(self.game.game_over)

if __name__ == '__main__':
    calculate_metrics('tetris_gemini.py')
    print("\n[UNIT TEST EXECUTION]")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTetrisGemini)
    unittest.TextTestRunner(verbosity=2).run(suite)