import random
import sys

# Basic constants
WHITE, BLACK = 'white', 'black'
FILES = 'ABCDEFGH'
RANKS = '12345678'


def opponent(color):
    return BLACK if color == WHITE else WHITE


def square_name(x, y):
    return f'{FILES[y]}{8 - x}'


class Spot:
    def __init__(self, x, y, piece=None):
        self.x = x  # row
        self.y = y  # col
        self.piece = piece

    def is_occupied(self):
        return self.piece is not None

    def __str__(self):
        if self.piece:
            return self.piece.symbol()
        return '.'


class Piece:
    def __init__(self, color):
        self.color = color

    def can_move(self, board, start, end):
        raise NotImplementedError

    def attacks(self, board, start, end):
        """Does this piece attack `end`? For most pieces this is the same as moving there."""
        return self.can_move(board, start, end)

    def is_opponent(self, other):
        return other and other.color != self.color

    def symbol(self):
        return '?'  # Placeholder


class King(Piece):
    def symbol(self):
        return 'K' if self.color == WHITE else 'k'

    def can_move(self, board, start, end):
        # Normal one-square moves. Castling is generated separately in Board.castling_moves,
        # because it is not an attack and needs extra checks.
        dx = abs(start.x - end.x)
        dy = abs(start.y - end.y)
        return max(dx, dy) == 1 and (not end.is_occupied() or self.is_opponent(end.piece))


class Queen(Piece):
    def symbol(self):
        return 'Q' if self.color == WHITE else 'q'

    def can_move(self, board, start, end):
        dx = end.x - start.x
        dy = end.y - start.y
        if (dx, dy) == (0, 0):
            return False
        if abs(dx) == abs(dy) or dx == 0 or dy == 0:
            return board.is_clear_path(start, end) and (not end.is_occupied() or self.is_opponent(end.piece))
        return False


class Rook(Piece):
    def symbol(self):
        return 'R' if self.color == WHITE else 'r'

    def can_move(self, board, start, end):
        dx = end.x - start.x
        dy = end.y - start.y
        if (dx, dy) == (0, 0):
            return False
        if dx == 0 or dy == 0:
            return board.is_clear_path(start, end) and (not end.is_occupied() or self.is_opponent(end.piece))
        return False


class Bishop(Piece):
    def symbol(self):
        return 'B' if self.color == WHITE else 'b'

    def can_move(self, board, start, end):
        dx = abs(end.x - start.x)
        dy = abs(end.y - start.y)
        if dx == dy and dx != 0:
            return board.is_clear_path(start, end) and (not end.is_occupied() or self.is_opponent(end.piece))
        return False


class Knight(Piece):
    def symbol(self):
        return 'N' if self.color == WHITE else 'n'

    def can_move(self, board, start, end):
        dx = abs(end.x - start.x)
        dy = abs(end.y - start.y)
        return dx * dy == 2 and (not end.is_occupied() or self.is_opponent(end.piece))


class Pawn(Piece):
    def symbol(self):
        return 'P' if self.color == WHITE else 'p'

    def direction(self):
        return -1 if self.color == WHITE else 1

    def can_move(self, board, start, end):
        dir = self.direction()
        start_row = 6 if self.color == WHITE else 1
        dx = end.x - start.x
        dy = abs(end.y - start.y)
        if dy == 0:
            if dx == dir and not end.is_occupied():
                return True
            if dx == 2 * dir and start.x == start_row and not end.is_occupied():
                intermediate = board.get_spot(start.x + dir, start.y)
                return not intermediate.is_occupied()
        elif dy == 1 and dx == dir:
            if end.is_occupied() and self.is_opponent(end.piece):
                return True
            # En passant: the square the enemy pawn just skipped over
            if not end.is_occupied() and board.en_passant == (end.x, end.y):
                return True
        return False

    def attacks(self, board, start, end):
        # Pawns move straight but capture diagonally.
        return abs(end.y - start.y) == 1 and end.x - start.x == self.direction()


PROMOTION_PIECES = {'Q': Queen, 'R': Rook, 'B': Bishop, 'N': Knight}


class Board:
    def __init__(self):
        self.grid = [[Spot(i, j) for j in range(8)] for i in range(8)]
        # Which sides each player may still castle to: K = king side, Q = queen side
        self.castling = {WHITE: {'K': True, 'Q': True}, BLACK: {'K': True, 'Q': True}}
        self.en_passant = None  # (row, col) a pawn can capture onto, or None
        self.setup_board()

    def setup_board(self):
        for y in range(8):
            self.grid[1][y].piece = Pawn(BLACK)
            self.grid[6][y].piece = Pawn(WHITE)
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for y, cls in enumerate(pieces):
            self.grid[0][y].piece = cls(BLACK)
            self.grid[7][y].piece = cls(WHITE)

    def clear(self):
        """Remove every piece (used to set up custom positions)."""
        for row in self.grid:
            for spot in row:
                spot.piece = None
        self.castling = {WHITE: {'K': False, 'Q': False}, BLACK: {'K': False, 'Q': False}}
        self.en_passant = None

    def print_board(self):
        for i in range(8):
            print(8 - i, end=' ')
            for j in range(8):
                print(self.grid[i][j], end=' ')
            print()
        print('  ' + ' '.join(FILES))

    def get_spot(self, x, y):
        return self.grid[x][y]

    def is_clear_path(self, start, end):
        dx = end.x - start.x
        dy = end.y - start.y
        step_x = (dx > 0) - (dx < 0)
        step_y = (dy > 0) - (dy < 0)
        x, y = start.x + step_x, start.y + step_y
        while (x, y) != (end.x, end.y):
            if self.grid[x][y].is_occupied():
                return False
            x += step_x
            y += step_y
        return True

    # --- Check / checkmate logic -------------------------------------------

    def find_king(self, color):
        for row in self.grid:
            for spot in row:
                if isinstance(spot.piece, King) and spot.piece.color == color:
                    return spot
        return None

    def is_attacked(self, target, by_color):
        """True if any piece of `by_color` attacks the square `target`."""
        for row in self.grid:
            for spot in row:
                if spot.is_occupied() and spot.piece.color == by_color:
                    if spot.piece.attacks(self, spot, target):
                        return True
        return False

    def in_check(self, color):
        king_spot = self.find_king(color)
        return king_spot is not None and self.is_attacked(king_spot, opponent(color))

    def castling_moves(self, color):
        """Castling is legal when: neither the king nor that rook has moved, the squares
        between them are empty, and the king is not in check, does not pass through an
        attacked square, and does not land on one."""
        row = 7 if color == WHITE else 0
        king = self.get_spot(row, 4)
        if not (isinstance(king.piece, King) and king.piece.color == color):
            return []
        enemy = opponent(color)
        if self.is_attacked(king, enemy):
            return []
        moves = []
        for side, rook_col, empty_cols, king_path in (('K', 7, (5, 6), (5, 6)),
                                                       ('Q', 0, (1, 2, 3), (3, 2))):
            if not self.castling[color][side]:
                continue
            rook = self.get_spot(row, rook_col).piece
            if not (isinstance(rook, Rook) and rook.color == color):
                continue
            if any(self.get_spot(row, c).is_occupied() for c in empty_cols):
                continue
            if any(self.is_attacked(self.get_spot(row, c), enemy) for c in king_path):
                continue
            moves.append(((row, 4), (row, king_path[-1])))
        return moves

    def pseudo_legal_moves(self, color):
        """Moves that follow piece rules, ignoring whether the king is left in check."""
        moves = []
        for x in range(8):
            for y in range(8):
                spot = self.get_spot(x, y)
                if spot.is_occupied() and spot.piece.color == color:
                    for i in range(8):
                        for j in range(8):
                            dest = self.get_spot(i, j)
                            if spot.piece.can_move(self, spot, dest):
                                moves.append(((x, y), (i, j)))
        return moves + self.castling_moves(color)

    def leaves_king_safe(self, move, color):
        """Try the move, see if our own king is in check, then undo it."""
        (sx, sy), (dx, dy) = move
        record = self.move_piece(self.get_spot(sx, sy), self.get_spot(dx, dy))
        safe = not self.in_check(color)
        self.undo_move(record)
        return safe

    def legal_moves(self, color):
        return [m for m in self.pseudo_legal_moves(color) if self.leaves_king_safe(m, color)]

    def all_valid_moves(self, color):
        # Kept for backwards compatibility; now returns only fully legal moves.
        return self.legal_moves(color)

    # --- Making moves -------------------------------------------------------

    def is_promotion(self, start, end):
        return isinstance(start.piece, Pawn) and end.x in (0, 7)

    def move_piece(self, start, end, promotion='Q'):
        """Make a move, including the special rules (castling, en passant, promotion).

        Returns a record that `undo_move` uses to restore the exact previous position.
        `record['captured']` is the captured piece, or None.
        """
        piece = start.piece
        record = {
            'changes': [],  # (spot, piece that was there before)
            'castling': {c: dict(r) for c, r in self.castling.items()},
            'en_passant': self.en_passant,
            'captured': end.piece,
            'special': None,
        }

        def place(spot, new_piece):
            record['changes'].append((spot, spot.piece))
            spot.piece = new_piece

        # En passant capture: the captured pawn is beside us, not on the target square.
        if isinstance(piece, Pawn) and start.y != end.y and not end.is_occupied():
            victim = self.get_spot(start.x, end.y)
            record['captured'] = victim.piece
            record['special'] = 'en passant'
            place(victim, None)

        place(start, None)
        place(end, piece)

        # Castling: the king moved two squares, so bring the rook across.
        if isinstance(piece, King) and abs(end.y - start.y) == 2:
            rook_from, rook_to = (7, 5) if end.y == 6 else (0, 3)
            rook_spot = self.get_spot(start.x, rook_from)
            rook = rook_spot.piece
            place(rook_spot, None)
            place(self.get_spot(start.x, rook_to), rook)
            record['special'] = 'castle'

        # Promotion: a pawn reaching the last rank becomes another piece.
        if isinstance(piece, Pawn) and end.x in (0, 7):
            place(end, PROMOTION_PIECES[promotion.upper()](piece.color))
            record['special'] = 'promotion'

        # Update castling rights.
        if isinstance(piece, King):
            self.castling[piece.color] = {'K': False, 'Q': False}
        for spot in (start, end):  # a rook moved away from, or was captured on, its corner
            for color, row in ((WHITE, 7), (BLACK, 0)):
                if spot.x == row and spot.y == 0:
                    self.castling[color]['Q'] = False
                if spot.x == row and spot.y == 7:
                    self.castling[color]['K'] = False

        # A pawn double step lets the opponent capture en passant on the next move only.
        self.en_passant = None
        if isinstance(piece, Pawn) and abs(end.x - start.x) == 2:
            self.en_passant = ((start.x + end.x) // 2, start.y)

        return record

    def undo_move(self, record):
        for spot, old_piece in reversed(record['changes']):
            spot.piece = old_piece
        self.castling = record['castling']
        self.en_passant = record['en_passant']


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = WHITE

    def parse_input(self, move_str):
        """Read 'E2 E4' (optionally 'E7 E8 N' for promotion) or 'O-O' / 'O-O-O'.
        Returns ((row, col), (row, col)) or (None, None)."""
        text = move_str.strip().upper().replace('0', 'O')
        if text in ('O-O', 'OO', 'O-O-O', 'OOO'):
            row = 7 if self.turn == WHITE else 0
            return (row, 4), (row, 6 if len(text.replace('-', '')) == 2 else 2)
        parts = text.split()
        if len(parts) == 3 and parts[2] in PROMOTION_PIECES:
            parts = parts[:2]
        if len(parts) != 2:
            return None, None
        src, dest = parts
        if len(src) != 2 or len(dest) != 2:
            return None, None
        if src[0] not in FILES or dest[0] not in FILES or src[1] not in RANKS or dest[1] not in RANKS:
            return None, None
        sy, sx = FILES.index(src[0]), 8 - int(src[1])
        dy, dx = FILES.index(dest[0]), 8 - int(dest[1])
        return (sx, sy), (dx, dy)

    def promotion_choice(self, move_str):
        parts = move_str.strip().upper().split()
        if len(parts) == 3 and parts[2] in PROMOTION_PIECES:
            return parts[2]
        while True:
            try:
                choice = input("Promote to (Q)ueen, (R)ook, (B)ishop or k(N)ight? ").strip().upper()
            except EOFError:
                return 'Q'
            if choice in PROMOTION_PIECES:
                return choice
            if choice == '':
                return 'Q'

    def describe(self, src, dest, record):
        text = f"{square_name(*src)} to {square_name(*dest)}"
        special = record['special']
        if special == 'castle':
            text += ' (castles king side)' if dest[1] == 6 else ' (castles queen side)'
        elif special == 'en passant':
            text += ' (en passant!)'
        elif special == 'promotion':
            text += f" (promotes to {type(self.board.get_spot(*dest).piece).__name__.lower()})"
        return text

    def check_game_over(self):
        """Called at the start of a turn. Returns True if the game has ended."""
        if self.board.legal_moves(self.turn):
            if self.board.in_check(self.turn):
                print("Check!")
            return False
        name = 'White' if self.turn == WHITE else 'Black'
        if self.board.in_check(self.turn):
            winner = 'Black' if self.turn == WHITE else 'White'
            print(f"Checkmate! {name} is mated — {winner} wins.")
        else:
            print(f"Stalemate! {name} has no legal moves — it's a draw.")
        return True

    def play(self):
        while True:
            self.board.print_board()
            print(f"Turn: {'White' if self.turn == WHITE else 'Black'}")
            if self.check_game_over():
                break
            if self.turn == WHITE:
                legal = self.board.legal_moves(WHITE)
                while True:
                    try:
                        move_str = input("Your move (e.g. E2 E4, O-O, or Q to quit): ")
                    except EOFError:
                        move_str = 'Q'
                    if move_str.strip().upper() in ('Q', 'QUIT'):
                        print("Goodbye!")
                        return
                    src, dest = self.parse_input(move_str)
                    if src and dest:
                        if (src, dest) in legal:
                            start, end = self.board.get_spot(*src), self.board.get_spot(*dest)
                            promo = self.promotion_choice(move_str) if self.board.is_promotion(start, end) else 'Q'
                            record = self.board.move_piece(start, end, promo)
                            print(f"You played: {self.describe(src, dest, record)}")
                            break
                        start = self.board.get_spot(*src)
                        end = self.board.get_spot(*dest)
                        if (start.is_occupied() and start.piece.color == WHITE
                                and start.piece.can_move(self.board, start, end)):
                            print("That move would leave your king in check.")
                            continue
                        if isinstance(start.piece, King) and abs(dest[1] - src[1]) == 2:
                            print("You can't castle right now.")
                            continue
                    print("Invalid move. Try again.")
            else:
                src, dest = random.choice(self.board.legal_moves(BLACK))
                record = self.board.move_piece(self.board.get_spot(*src), self.board.get_spot(*dest))
                print(f"Computer played: {self.describe(src, dest, record)}")
            self.turn = opponent(self.turn)


def main_menu():
    while True:
        print()
        print('=' * 34)
        print('        ♞  TERMINAL CHESS')
        print('=' * 34)
        print('  1. Play against the computer')
        print('  2. Chess Academy (openings, traps, puzzles)')
        print('  Q. Quit')
        try:
            choice = input('> ').strip().lower()
        except EOFError:
            return
        if choice == '1':
            Game().play()
        elif choice == '2':
            import academy  # imported lazily so chess.py also works on its own
            academy.academy()
        elif choice in ('q', 'quit'):
            print('Goodbye!')
            return


if __name__ == '__main__':
    main_menu()
