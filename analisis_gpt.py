import unittest
import pygame
import sys
import os


try:

    from tetris_gpt import Tetris, create_grid, PIECES, COLS, ROWS, valid_position
except ImportError:
    print("Error: File 'tetris_gpt.py' tidak ditemukan.")
    print("Pastikan nama file kode game adalah 'tetris_gpt.py'.")
    sys.exit(1)


def calculate_metrics(filename):
    print("\n" + "="*50)
    print(f"[{filename}] ANALISIS METRIK KODE (GPT-5 PRO)")
    print("="*50)
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
    print("="*50 + "\n")


class TestTetrisGPT(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pygame.init()

        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def setUp(self):
        self.game = Tetris()



    def test_t1_board_initialization(self):

        self.assertEqual(len(self.game.grid), ROWS)
        self.assertEqual(len(self.game.grid[0]), COLS)
        self.assertTrue(all(cell is None for row in self.game.grid for cell in row))


    def test_t2_block_spawning(self):

        self.assertIsNotNone(self.game.current)

        self.assertEqual(self.game.current['x'], 3)
        self.assertEqual(self.game.current['y'], -2)
        self.assertIn(self.game.current['letter'], PIECES.keys())


    def test_t3_horizontal_movement(self):

        self.game.current['x'] = 4
        self.game.current['y'] = 5 
        initial_x = self.game.current['x']
        

        self.game.move(-1) 
        self.assertEqual(self.game.current['x'], initial_x - 1)
        

        self.game.move(1)
        self.assertEqual(self.game.current['x'], initial_x)


    def test_t4_simple_rotation(self):

        self.game.current['letter'] = 'T'
        self.game.current['rot'] = 0
        self.game.current['x'] = 4
        self.game.current['y'] = 5
        

        self.game.rotate(cw=True)
        self.assertEqual(self.game.current['rot'], 1)
        

        self.game.rotate(cw=False)
        self.assertEqual(self.game.current['rot'], 0)


    def test_t5_bottom_collision(self):

        self.game.current['letter'] = 'I'
        self.game.current['rot'] = 0

        self.game.current['y'] = ROWS - 3
        self.game.current['x'] = 3
        

        moved = self.game.drop_one()
        
        self.assertFalse(moved, "Piece seharusnya tidak bisa turun lagi (collision)")
        

        row_filled = any(cell is not None for cell in self.game.grid[ROWS-1])
        self.assertTrue(row_filled, "Grid paling bawah harus terisi blok")


    def test_t6_lateral_collision(self):

        self.game.current['letter'] = 'I'
        self.game.current['rot'] = 1 

        self.game.current['x'] = -2 
        self.game.current['y'] = 5
        
        initial_x = self.game.current['x']
        

        self.game.move(-1)
        
        self.assertEqual(self.game.current['x'], initial_x, "Tidak boleh tembus dinding kiri")

    def test_t7_wall_kick_rotation(self):

        self.game.current['letter'] = 'I'
        self.game.current['rot'] = 1 

        self.game.current['x'] = 7 
        self.game.current['y'] = 5
        

        
        self.game.rotate(cw=True)
        

        self.assertEqual(self.game.current['rot'], 2)

        self.assertTrue(self.game.current['x'] < 7, "Piece harusnya 'ditendang' ke kiri agar muat")


    def test_t8_line_clearing(self):

        self.game.grid[ROWS-1] = ['I'] * COLS
        

        from tetris_gpt import clear_lines
        cleared_count = clear_lines(self.game.grid)
        
        self.assertEqual(cleared_count, 1)

        self.assertTrue(all(c is None for c in self.game.grid[0]))
        self.assertEqual(len(self.game.grid), ROWS)


    def test_t9_scoring_system(self):
        self.game.level = 1
        self.game.score = 0
        

        from tetris_gpt import SCORES_PER_LINES
        lines_cleared = 2
        

        points = SCORES_PER_LINES[lines_cleared] * self.game.level
        self.game.score += points
        
        self.assertEqual(self.game.score, 300)


    def test_t10_game_over(self):

        self.game.grid[0] = ['X'] * COLS
        

        self.game.spawn_new_piece()
        

        self.assertTrue(self.game.game_over, "Spawn di area penuh harus trigger Game Over")

if __name__ == '__main__':

    print("\n" + "="*50)
    print("[UNIT TEST EXECUTION - GPT-5 PRO]")
    print("="*50)
    

    suite = unittest.TestLoader().loadTestsFromTestCase(TestTetrisGPT)
    

    result = unittest.TextTestRunner(verbosity=2).run(suite)


    calculate_metrics('tetris_gpt.py')