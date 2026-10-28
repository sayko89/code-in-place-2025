"""Checks that every Academy lesson is playable with the game engine.

Run with:  python3 -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess  # noqa: E402
from academy import board_from_fen, play_line, square  # noqa: E402
from lessons import OPENINGS, PUZZLES, TRAPS  # noqa: E402


class LessonTests(unittest.TestCase):
    def test_openings_are_legal(self):
        for lesson in OPENINGS:
            with self.subTest(lesson['name']):
                play_line(lesson['moves'], len(lesson['moves']))

    def test_traps_are_legal(self):
        for lesson in TRAPS:
            with self.subTest(lesson['name']):
                play_line(lesson['moves'], len(lesson['moves']))

    def test_mating_traps_end_in_checkmate(self):
        for lesson in TRAPS:
            if not lesson['moves'][-1][1].endswith('#'):
                continue
            with self.subTest(lesson['name']):
                board, to_move, _ = play_line(lesson['moves'], len(lesson['moves']))
                self.assertTrue(board.in_check(to_move))
                self.assertEqual(board.legal_moves(to_move), [])

    def test_puzzle_solutions(self):
        for p in PUZZLES:
            with self.subTest(p['name']):
                board = board_from_fen(p['fen'])
                color = chess.WHITE if p['to_move'] == 'white' else chess.BLACK
                src, dst = square(p['solution'][:2]), square(p['solution'][2:])
                self.assertIn((src, dst), board.legal_moves(color))
                board.move_piece(board.get_spot(*src), board.get_spot(*dst))
                other = chess.opponent(color)
                self.assertTrue(board.in_check(other))
                if p['goal'] == 'mate':
                    self.assertEqual(board.legal_moves(other), [])
                else:
                    self.assertNotEqual(board.legal_moves(other), [])


class EngineTests(unittest.TestCase):
    def test_opening_position_has_20_moves(self):
        self.assertEqual(len(chess.Board().legal_moves(chess.WHITE)), 20)

    def test_stalemate(self):
        board = board_from_fen('7k/5K2/6Q1/8/8/8/8/8')
        self.assertFalse(board.in_check(chess.BLACK))
        self.assertEqual(board.legal_moves(chess.BLACK), [])

    def test_pinned_piece_cannot_leave_the_line(self):
        board = board_from_fen('k3r3/8/8/8/8/8/4R3/4K3')
        rook_moves = [m for m in board.legal_moves(chess.WHITE) if m[0] == square('e2')]
        self.assertTrue(rook_moves)
        self.assertTrue(all(dst[1] == 4 for _, dst in rook_moves))


if __name__ == '__main__':
    unittest.main()
