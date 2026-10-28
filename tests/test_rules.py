"""Tests for the special rules: castling, en passant and promotion.

The perft tests count every position reachable to a given depth and compare the
totals with well-known reference numbers (https://www.chessprogramming.org/Perft_Results).
If any rule were even slightly wrong, these counts would not match.

Run with:  python3 -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chess  # noqa: E402
from academy import board_from_fen, square  # noqa: E402


def play(board, *moves):
    """Play moves like 'e2e4' (alternating colours, White first) and return the last record."""
    record = None
    color = chess.WHITE
    for m in moves:
        src, dst = square(m[:2]), square(m[2:4])
        assert (src, dst) in board.legal_moves(color), f'{m} should be legal'
        record = board.move_piece(board.get_spot(*src), board.get_spot(*dst),
                                  m[4].upper() if len(m) > 4 else 'Q')
        color = chess.opponent(color)
    return record


def perft(board, color, depth):
    if depth == 0:
        return 1
    total = 0
    for src, dst in board.legal_moves(color):
        start, end = board.get_spot(*src), board.get_spot(*dst)
        options = 'QRBN' if board.is_promotion(start, end) else 'Q'
        for promo in options:
            record = board.move_piece(start, end, promo)
            total += perft(board, chess.opponent(color), depth - 1)
            board.undo_move(record)
    return total


class CastlingTests(unittest.TestCase):
    def test_king_side_castling_moves_the_rook(self):
        board = chess.Board()
        play(board, 'e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1c4', 'f8c5')
        self.assertIn((square('e1'), square('g1')), board.legal_moves(chess.WHITE))
        board.move_piece(board.get_spot(*square('e1')), board.get_spot(*square('g1')))
        self.assertIsInstance(board.get_spot(*square('g1')).piece, chess.King)
        self.assertIsInstance(board.get_spot(*square('f1')).piece, chess.Rook)
        self.assertIsNone(board.get_spot(*square('h1')).piece)

    def test_queen_side_castling(self):
        board = board_from_fen('r3k3/8/8/8/8/8/8/R3K3 w Qq -')
        board.move_piece(board.get_spot(*square('e1')), board.get_spot(*square('c1')))
        self.assertIsInstance(board.get_spot(*square('c1')).piece, chess.King)
        self.assertIsInstance(board.get_spot(*square('d1')).piece, chess.Rook)

    def test_no_castling_out_of_through_or_into_check(self):
        for fen in ('4r1k1/8/8/8/8/8/8/4K2R w K -',    # in check
                    '5rk1/8/8/8/8/8/8/4K2R w K -',     # passes through f1
                    '6rk/8/8/8/8/8/8/4K2R w K -'):     # lands on g1
            board = board_from_fen(fen)
            self.assertNotIn((square('e1'), square('g1')), board.legal_moves(chess.WHITE), fen)

    def test_no_castling_after_king_moved(self):
        board = board_from_fen('4k3/8/8/8/8/8/8/4K2R w K -')
        play(board, 'e1f1', 'e8d8', 'f1e1', 'd8e8')
        self.assertNotIn((square('e1'), square('g1')), board.legal_moves(chess.WHITE))

    def test_no_castling_through_pieces(self):
        board = chess.Board()
        self.assertNotIn((square('e1'), square('g1')), board.legal_moves(chess.WHITE))


class EnPassantTests(unittest.TestCase):
    def test_en_passant_capture(self):
        board = chess.Board()
        play(board, 'e2e4', 'a7a6', 'e4e5', 'd7d5')
        self.assertIn((square('e5'), square('d6')), board.legal_moves(chess.WHITE))
        record = board.move_piece(board.get_spot(*square('e5')), board.get_spot(*square('d6')))
        self.assertEqual(record['special'], 'en passant')
        self.assertIsNone(board.get_spot(*square('d5')).piece)

    def test_en_passant_only_on_the_next_move(self):
        board = chess.Board()
        play(board, 'e2e4', 'a7a6', 'e4e5', 'd7d5', 'h2h3', 'h7h6')
        self.assertNotIn((square('e5'), square('d6')), board.legal_moves(chess.WHITE))


class PromotionTests(unittest.TestCase):
    def test_promotion_and_undo(self):
        board = board_from_fen('8/4P3/8/8/8/8/8/k6K')
        start, end = board.get_spot(*square('e7')), board.get_spot(*square('e8'))
        record = board.move_piece(start, end, 'N')
        self.assertIsInstance(end.piece, chess.Knight)
        self.assertEqual(end.piece.color, chess.WHITE)
        board.undo_move(record)
        self.assertIsInstance(start.piece, chess.Pawn)
        self.assertIsNone(end.piece)

    def test_default_promotion_is_a_queen(self):
        board = board_from_fen('8/4P3/8/8/8/8/8/k6K')
        board.move_piece(board.get_spot(*square('e7')), board.get_spot(*square('e8')))
        self.assertIsInstance(board.get_spot(*square('e8')).piece, chess.Queen)


class InputTests(unittest.TestCase):
    def test_castling_notation(self):
        game = chess.Game()
        self.assertEqual(game.parse_input('O-O'), (square('e1'), square('g1')))
        self.assertEqual(game.parse_input('0-0-0'), (square('e1'), square('c1')))

    def test_promotion_notation(self):
        game = chess.Game()
        self.assertEqual(game.parse_input('E7 E8 N'), (square('e7'), square('e8')))


class PerftTests(unittest.TestCase):
    def test_start_position(self):
        self.assertEqual(perft(chess.Board(), chess.WHITE, 3), 8902)

    def test_kiwipete(self):
        # Castling on both sides, pins, en passant opportunities
        board = board_from_fen('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -')
        self.assertEqual(perft(board, chess.WHITE, 2), 2039)

    def test_en_passant_endgame(self):
        board = board_from_fen('8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -')
        self.assertEqual(perft(board, chess.WHITE, 3), 2812)

    def test_promotions(self):
        board = board_from_fen('r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq -')
        self.assertEqual(perft(board, chess.WHITE, 2), 264)


if __name__ == '__main__':
    unittest.main()
