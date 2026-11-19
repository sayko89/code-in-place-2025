"""Checks the New Year's Eve mode: every countdown puzzle is a real mate in 1.

Run with:  python3 -m unittest discover tests
"""
import datetime
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess  # noqa: E402
import winter  # noqa: E402
from academy import board_from_fen, coord_move  # noqa: E402
from lessons import NEW_YEAR_PUZZLES  # noqa: E402


class CountdownPuzzleTests(unittest.TestCase):
    def test_twelve_chimes(self):
        self.assertEqual(len(NEW_YEAR_PUZZLES), 12)

    def test_positions_are_legal(self):
        for p in NEW_YEAR_PUZZLES:
            with self.subTest(p['name']):
                board = board_from_fen(p['fen'])
                self.assertIsNotNone(board.find_king(chess.WHITE))
                self.assertIsNotNone(board.find_king(chess.BLACK))
                self.assertFalse(board.in_check(chess.BLACK), 'side not to move is in check')

    def test_solutions_are_checkmate(self):
        for p in NEW_YEAR_PUZZLES:
            with self.subTest(p['name']):
                board = board_from_fen(p['fen'])
                src, dst, promo = coord_move(p['solution'])
                self.assertIn((src, dst), board.legal_moves(chess.WHITE))
                board.move_piece(board.get_spot(*src), board.get_spot(*dst), promo)
                self.assertTrue(board.in_check(chess.BLACK))
                self.assertEqual(board.legal_moves(chess.BLACK), [])
                self.assertTrue(p['san'].endswith('#'))


class ClockAndAnimationTests(unittest.TestCase):
    def test_clock_reaches_midnight_on_the_twelfth_chime(self):
        self.assertEqual(winter.clock(0), '23:48')
        self.assertEqual(winter.clock(11), '23:59')
        self.assertEqual(winter.clock(12), '00:00')

    def test_new_year(self):
        self.assertEqual(winter.new_year(datetime.date(2026, 12, 31)), 2027)
        self.assertEqual(winter.new_year(datetime.date(2026, 11, 20)), 2027)
        self.assertEqual(winter.new_year(datetime.date(2027, 1, 1)), 2027)

    def test_snow_stays_inside_the_frame(self):
        rng = random.Random(1)
        flakes = winter.new_flakes(20, 6, 15, rng)
        for _ in range(30):
            winter.fall(flakes, 20, 6, rng)
            frame = winter.snow_frame(20, 6, flakes, ['HI'])
            self.assertEqual(len(frame), 6)
            self.assertTrue(all(len(row) == 20 for row in frame))
            self.assertIn('HI', frame[2])


if __name__ == '__main__':
    unittest.main()
