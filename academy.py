"""Chess Academy — learn openings, traps and tactics in the terminal.

Lessons are replayed move by move on a real board driven by the game engine,
so every move shown is a legal move in this program.
"""
import os
import sys

import chess
from lessons import OPENINGS, TRAPS, PUZZLES, TIPS

# ---------------------------------------------------------------------------
# Terminal styling
# ---------------------------------------------------------------------------
USE_COLOR = sys.stdout.isatty() and os.environ.get('NO_COLOR') is None

GLYPHS = {chess.King: '♚', chess.Queen: '♛', chess.Rook: '♜',
          chess.Bishop: '♝', chess.Knight: '♞', chess.Pawn: '♟'}


def style(text, *codes):
    if not USE_COLOR:
        return text
    return f"\033[{';'.join(str(c) for c in codes)}m{text}\033[0m"


def bold(text):
    return style(text, 1)


def dim(text):
    return style(text, 2)


def accent(text):
    return style(text, 1, 36)


def good(text):
    return style(text, 1, 32)


def bad(text):
    return style(text, 1, 31)


def clear_screen():
    if USE_COLOR:
        print('\033[2J\033[H', end='')
    else:
        print('\n' + '-' * 50)


def render_board(board, highlight=(), check=None):
    """Print the board. Uses coloured squares and chess glyphs on a real terminal,
    and falls back to the plain letter board otherwise."""
    if not USE_COLOR:
        board.print_board()
        return
    light, dark = 223, 137          # 256-colour palette
    hl_light, hl_dark = 229, 185
    for r in range(8):
        line = dim(f' {8 - r} ')
        for c in range(8):
            is_light = (r + c) % 2 == 0
            bg = light if is_light else dark
            if (r, c) in highlight:
                bg = hl_light if is_light else hl_dark
            if check == (r, c):
                bg = 203
            piece = board.get_spot(r, c).piece
            if piece:
                fg = '38;5;231' if piece.color == chess.WHITE else '38;5;16'
                cell = f'\033[48;5;{bg};{fg};1m {GLYPHS[type(piece)]} \033[0m'
            else:
                cell = f'\033[48;5;{bg}m   \033[0m'
            line += cell
        print(line)
    print(dim('    ' + '  '.join(chess.FILES)))


# ---------------------------------------------------------------------------
# Engine helpers
# ---------------------------------------------------------------------------

def square(name):
    """'e2' -> (row, col)"""
    return 8 - int(name[1]), chess.FILES.index(name[0].upper())


def parse_move(text):
    """Accepts 'e2e4', 'E2 E4' or 'e2-e4'."""
    cleaned = text.strip().lower().replace(' ', '').replace('-', '')
    if len(cleaned) != 4 or cleaned[0] not in 'abcdefgh' or cleaned[2] not in 'abcdefgh' \
            or cleaned[1] not in chess.RANKS or cleaned[3] not in chess.RANKS:
        return None
    return square(cleaned[:2]), square(cleaned[2:])


PIECES_BY_LETTER = {'k': chess.King, 'q': chess.Queen, 'r': chess.Rook,
                    'b': chess.Bishop, 'n': chess.Knight, 'p': chess.Pawn}


def board_from_fen(placement):
    """Build a Board from the piece-placement field of a FEN string."""
    board = chess.Board()
    for row in board.grid:
        for spot in row:
            spot.piece = None
    for r, rank in enumerate(placement.split('/')):
        c = 0
        for ch in rank:
            if ch.isdigit():
                c += int(ch)
            else:
                color = chess.WHITE if ch.isupper() else chess.BLACK
                board.get_spot(r, c).piece = PIECES_BY_LETTER[ch.lower()](color)
                c += 1
    return board


def play_line(moves, upto):
    """Return a fresh board with the first `upto` moves of a lesson played.
    Raises ValueError if a move is illegal (used by the tests)."""
    board = chess.Board()
    color = chess.WHITE
    last = None
    for coord, san, _ in moves[:upto]:
        src, dst = square(coord[:2]), square(coord[2:])
        if (src, dst) not in board.legal_moves(color):
            raise ValueError(f'Illegal move in lesson: {san} ({coord})')
        board.move_piece(board.get_spot(*src), board.get_spot(*dst))
        last = (src, dst)
        color = chess.opponent(color)
    return board, color, last


def king_in_check(board, color):
    if board.in_check(color):
        k = board.find_king(color)
        return (k.x, k.y)
    return None


def move_number(i):
    n = i // 2 + 1
    return f'{n}.' if i % 2 == 0 else f'{n}...'


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        return 'q'


def lesson_viewer(lesson, kind):
    moves = lesson['moves']
    i = 0
    while True:
        clear_screen()
        board, to_move, last = play_line(moves, i)
        print(accent(f"  {kind}: {lesson['name']}"))
        print(dim(f"  {lesson['summary']}"))
        print()
        render_board(board, highlight=last or (), check=king_in_check(board, to_move))
        print()

        played = '  '.join(f'{move_number(j)} {m[1]}' if j % 2 == 0 else m[1]
                           for j, m in enumerate(moves[:i]))
        print('  ' + (played or dim('(starting position)')))
        if i > 0:
            coord, san, note = moves[i - 1]
            print()
            print(f"  {bold(move_number(i - 1) + ' ' + san)}  {note}")
        if i == len(moves):
            print()
            if board.in_check(to_move) and not board.legal_moves(to_move):
                print('  ' + bad('Checkmate!'))
            print('  ' + good('End of line.'))

        print()
        print(dim(f'  move {i}/{len(moves)}  ·  [Enter] next  [b] back  [r] restart  [q] menu'))
        cmd = ask('  > ').strip().lower()
        if cmd == 'q':
            return
        if cmd == 'b':
            i = max(0, i - 1)
        elif cmd == 'r':
            i = 0
        elif i < len(moves):
            i += 1
        else:
            return


def puzzle_screen(puzzle, number, total):
    board = board_from_fen(puzzle['fen'])
    color = chess.WHITE if puzzle['to_move'] == 'white' else chess.BLACK
    message = ''
    while True:
        clear_screen()
        print(accent(f"  Puzzle {number}/{total}: {puzzle['name']}"))
        print(dim(f"  {puzzle['theme']}  ·  {puzzle['to_move'].capitalize()} to move"))
        print()
        render_board(board)
        print()
        if message:
            print('  ' + message)
            print()
        print(dim('  Type a move like D1 D8  ·  [h] hint  [s] show solution  [q] menu'))
        text = ask('  > ').strip()
        cmd = text.lower()
        if cmd == 'q':
            return False
        if cmd == 'h':
            message = 'Hint: ' + puzzle['hint']
            continue
        if cmd == 's':
            reveal(board, puzzle, color, solved=False)
            return True
        move = parse_move(text)
        if not move:
            message = bad('Could not read that move. Example: D1 D8')
            continue
        if move not in board.legal_moves(color):
            message = bad('That move is not legal here. Try again.')
            continue
        src, dst = move
        if move == (square(puzzle['solution'][:2]), square(puzzle['solution'][2:])):
            reveal(board, puzzle, color, solved=True)
            return True
        if puzzle['goal'] == 'mate':
            captured = board.move_piece(board.get_spot(*src), board.get_spot(*dst))
            mated = board.in_check(chess.opponent(color)) and not board.legal_moves(chess.opponent(color))
            board.undo_move(board.get_spot(*src), board.get_spot(*dst), captured)
            if mated:
                reveal(board, puzzle, color, solved=True)
                return True
        message = bad('Legal, but not the best move. Try again!')


def reveal(board, puzzle, color, solved):
    src = square(puzzle['solution'][:2])
    dst = square(puzzle['solution'][2:])
    board.move_piece(board.get_spot(*src), board.get_spot(*dst))
    clear_screen()
    print(accent(f"  {puzzle['name']}"))
    print()
    render_board(board, highlight=(src, dst), check=king_in_check(board, chess.opponent(color)))
    print()
    print('  ' + (good('Correct!  ') if solved else dim('Solution: ')) + bold(puzzle['san']))
    print('  ' + puzzle['explanation'])
    print()
    ask(dim('  [Enter] continue '))


def puzzles_menu():
    for n, puzzle in enumerate(PUZZLES, 1):
        if not puzzle_screen(puzzle, n, len(PUZZLES)):
            return
    clear_screen()
    print(good('  You finished all the puzzles!'))
    ask(dim('  [Enter] back to menu '))


def tips_screen():
    clear_screen()
    print(accent('  10 principles every player should know'))
    print()
    for n, (title, text) in enumerate(TIPS, 1):
        print(f'  {bold(f"{n:>2}. {title}")}')
        print(f'      {text}')
    print()
    ask(dim('  [Enter] back to menu '))


def pick_from(items, title, kind):
    while True:
        clear_screen()
        print(accent(f'  {title}'))
        print()
        for n, item in enumerate(items, 1):
            print(f"  {bold(str(n).rjust(2))}. {item['name']}")
            print(f"      {dim(item['summary'])}")
        print()
        choice = ask(dim('  Choose a number, or [q] back: ')).strip().lower()
        if choice == 'q':
            return
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            lesson_viewer(items[int(choice) - 1], kind)


def academy():
    while True:
        clear_screen()
        print(accent('  ♞  CHESS ACADEMY'))
        print(dim('  Learn the ideas, then use them against the computer.'))
        print()
        print(f'  {bold("1")}. Openings      {dim(f"{len(OPENINGS)} lines with move-by-move notes")}')
        print(f'  {bold("2")}. Traps         {dim(f"{len(TRAPS)} famous traps and how they work")}')
        print(f'  {bold("3")}. Puzzles       {dim(f"{len(PUZZLES)} find-the-move challenges")}')
        print(f'  {bold("4")}. Principles    {dim("10 rules of thumb")}')
        print(f'  {bold("Q")}. Back')
        print()
        choice = ask('  > ').strip().lower()
        if choice == '1':
            pick_from(OPENINGS, 'Openings', 'Opening')
        elif choice == '2':
            pick_from(TRAPS, 'Traps', 'Trap')
        elif choice == '3':
            puzzles_menu()
        elif choice == '4':
            tips_screen()
        elif choice in ('q', 'quit'):
            return


if __name__ == '__main__':
    academy()
