import random
import sys

# Basic constants
WHITE, BLACK = 'white', 'black'
FILES = 'ABCDEFGH'
RANKS = '12345678'


def opponent(color):
    return BLACK if color == WHITE else WHITE


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

    def is_opponent(self, other):
        return other and other.color != self.color

    def symbol(self):
        return '?'  # Placeholder


class King(Piece):
    def symbol(self):
        return 'K' if self.color == WHITE else 'k'

    def can_move(self, board, start, end):
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

    def can_move(self, board, start, end):
        dir = -1 if self.color == WHITE else 1
        start_row = 6 if self.color == WHITE else 1
        dx = end.x - start.x
        dy = abs(end.y - start.y)
        if dy == 0:
            if dx == dir and not end.is_occupied():
                return True
            if dx == 2 * dir and start.x == start_row and not end.is_occupied():
                intermediate = board.get_spot(start.x + dir, start.y)
                return not intermediate.is_occupied()
        elif dy == 1 and dx == dir and end.is_occupied() and self.is_opponent(end.piece):
            return True
        return False


class Board:
    def __init__(self):
        self.grid = [[Spot(i, j) for j in range(8)] for i in range(8)]
        self.setup_board()

    def setup_board(self):
        for y in range(8):
            self.grid[1][y].piece = Pawn(BLACK)
            self.grid[6][y].piece = Pawn(WHITE)
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for y, cls in enumerate(pieces):
            self.grid[0][y].piece = cls(BLACK)
            self.grid[7][y].piece = cls(WHITE)

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
        """True if any piece of `by_color` could move onto `target`."""
        for row in self.grid:
            for spot in row:
                if spot.is_occupied() and spot.piece.color == by_color:
                    if spot.piece.can_move(self, spot, target):
                        return True
        return False

    def in_check(self, color):
        king_spot = self.find_king(color)
        return king_spot is not None and self.is_attacked(king_spot, opponent(color))

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
        return moves

    def leaves_king_safe(self, move, color):
        """Try the move, see if our own king is in check, then undo it."""
        (sx, sy), (dx, dy) = move
        start, end = self.get_spot(sx, sy), self.get_spot(dx, dy)
        captured = self.move_piece(start, end)
        safe = not self.in_check(color)
        self.undo_move(start, end, captured)
        return safe

    def legal_moves(self, color):
        return [m for m in self.pseudo_legal_moves(color) if self.leaves_king_safe(m, color)]

    def all_valid_moves(self, color):
        # Kept for backwards compatibility; now returns only fully legal moves.
        return self.legal_moves(color)

    # --- Making moves -------------------------------------------------------

    def move_piece(self, start, end):
        """Move a piece and return whatever was captured (or None)."""
        captured = end.piece
        end.piece = start.piece
        start.piece = None
        return captured

    def undo_move(self, start, end, captured):
        start.piece = end.piece
        end.piece = captured


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = WHITE

    def parse_input(self, move_str):
        try:
            src, dest = move_str.strip().upper().split()
            if len(src) != 2 or len(dest) != 2:
                return None, None
            if src[1] not in RANKS or dest[1] not in RANKS:
                return None, None
            sy, sx = FILES.index(src[0]), 8 - int(src[1])
            dy, dx = FILES.index(dest[0]), 8 - int(dest[1])
            return (sx, sy), (dx, dy)
        except ValueError:
            return None, None

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
                        move_str = input("Your move (e.g., E2 E4, or Q to quit): ")
                    except EOFError:
                        move_str = 'Q'
                    if move_str.strip().upper() in ('Q', 'QUIT'):
                        print("Goodbye!")
                        return
                    src, dest = self.parse_input(move_str)
                    if src and dest:
                        if (src, dest) in legal:
                            self.board.move_piece(self.board.get_spot(*src), self.board.get_spot(*dest))
                            break
                        start = self.board.get_spot(*src)
                        if (start.is_occupied() and start.piece.color == WHITE
                                and start.piece.can_move(self.board, start, self.board.get_spot(*dest))):
                            print("That move would leave your king in check.")
                            continue
                    print("Invalid move. Try again.")
            else:
                src, dest = random.choice(self.board.legal_moves(BLACK))
                self.board.move_piece(self.board.get_spot(*src), self.board.get_spot(*dest))
                print(f"Computer played: {FILES[src[1]]}{8-src[0]} to {FILES[dest[1]]}{8-dest[0]}")
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
