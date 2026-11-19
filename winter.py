"""New Year's Eve mode — a seasonal extra for Chess Lab.

* A snowfall intro.
* "Countdown to Midnight": twelve checkmate-in-1 puzzles. Each one you finish moves
  the clock a minute closer to midnight; the twelfth chime sets off fireworks.
* A game against the computer on a snowy board.

Every puzzle is checked against the engine by `tests/test_winter.py`.
"""
import datetime
import random
import time

import academy
import chess
from academy import accent, ask, bad, bold, clear_screen, dim, good, style
from lessons import NEW_YEAR_PUZZLES

# Icy squares: light, dark, highlighted light, highlighted dark (gold), check
WINTER = (110, 67, 222, 179, 203)

FLAKES = '*+.·'
SPARKS = '*+·o'
FIREWORK_COLORS = (196, 214, 226, 46, 51, 201)


def new_year(today=None):
    """The year we are counting down to: next year from July on, this year until June."""
    today = today or datetime.date.today()
    return today.year + 1 if today.month >= 7 else today.year


def clock(chimes):
    """'23:48' before the first chime, '00:00' after the twelfth."""
    minutes = 23 * 60 + 48 + chimes
    return f'{minutes // 60 % 24:02d}:{minutes % 60:02d}'


# ---------------------------------------------------------------------------
# Snow and fireworks (pure functions build the frames; the loops just print them)
# ---------------------------------------------------------------------------

def new_flakes(width, height, count, rng):
    return [[rng.randrange(height), rng.randrange(width), rng.choice(FLAKES)] for _ in range(count)]


def fall(flakes, width, height, rng):
    """Move every flake down one row, drifting a little; flakes leaving the bottom restart at the top."""
    for flake in flakes:
        flake[0] += 1
        flake[1] = (flake[1] + rng.choice((-1, 0, 0, 1))) % width
        if flake[0] >= height:
            flake[0], flake[1] = 0, rng.randrange(width)


def snow_frame(width, height, flakes, message=()):
    """Return the frame as a list of strings: snowflakes with `message` lines centered on top."""
    rows = [[' '] * width for _ in range(height)]
    for r, c, ch in flakes:
        if 0 <= r < height and 0 <= c < width:
            rows[r][c] = ch
    top = (height - len(message)) // 2
    for i, line in enumerate(message):
        start = max(0, (width - len(line)) // 2)
        for j, ch in enumerate(line[:width]):
            rows[top + i][start + j] = ch
    return [''.join(row) for row in rows]


def firework_frame(width, height, bursts, step):
    """Each burst is (row, col, color). At `step` its sparks sit `step` squares from the center."""
    rows = [[' '] * width for _ in range(height)]
    colors = {}
    for r, c, color in bursts:
        for dr, dc in ((-1, 0), (1, 0), (0, -2), (0, 2), (-1, -2), (-1, 2), (1, -2), (1, 2)):
            rr, cc = r + dr * step, c + dc * step
            if 0 <= rr < height and 0 <= cc < width:
                rows[rr][cc] = SPARKS[min(step, len(SPARKS) - 1)]
                colors[(rr, cc)] = color
    return rows, colors


def snow_intro(year, seconds=2.5):
    title = [f'❄  NEW YEAR\'S EVE {year}  ❄', '', 'Chess Lab · winter edition']
    if not academy.USE_COLOR:
        print('\n'.join(title))
        return
    width, height, rng = 46, 13, random.Random()
    flakes = new_flakes(width, height, 40, rng)
    for _ in range(int(seconds / 0.12)):
        clear_screen()
        for line in snow_frame(width, height, flakes, title):
            print('  ' + style(line, 1, 38, 5, 195))
        fall(flakes, width, height, rng)
        time.sleep(0.12)


def fireworks(year, seconds=3.0):
    message = f'✦  HAPPY NEW YEAR {year}!  ✦'
    if not academy.USE_COLOR:
        print(message)
        return
    width, height, rng = 46, 13, random.Random()
    bursts, step = [], 0
    for tick in range(int(seconds / 0.15)):
        if tick % 4 == 0:  # launch a new rocket every few frames
            bursts.append((rng.randrange(2, height - 2), rng.randrange(4, width - 4), rng.choice(FIREWORK_COLORS)))
            bursts = bursts[-3:]
        step = tick % 4
        rows, colors = firework_frame(width, height, bursts, step)
        clear_screen()
        for r in range(height):
            print('  ' + ''.join(style(ch, 1, 38, 5, colors[(r, c)]) if (r, c) in colors else ch
                                 for c, ch in enumerate(rows[r])))
        print()
        print('  ' + accent(message.center(width)))
        time.sleep(0.15)


# ---------------------------------------------------------------------------
# Countdown to Midnight
# ---------------------------------------------------------------------------

def chime_bar(done, total):
    return ' '.join(good('●') if i < done else dim('○') for i in range(total))


def countdown_puzzle(puzzle, number, total):
    """Returns 'star' (solved first try, no hint), 'solved', 'shown' or 'quit'."""
    board = academy.board_from_fen(puzzle['fen'])
    solution = academy.coord_move(puzzle['solution'])
    message, clean = '', True
    while True:
        clear_screen()
        print(accent(f"  {clock(number - 1)}") + dim(f"  ·  chime {number} of {total}"))
        print('  ' + chime_bar(number - 1, total))
        print()
        print(bold(f"  {puzzle['name']}") + dim('  ·  White to move and mate in 1'))
        print()
        academy.render_board(board, palette=WINTER)
        print()
        if message:
            print('  ' + message)
            print()
        print(dim('  Type a move like D1 D8  ·  [h] hint  [s] show solution  [q] menu'))
        text = ask('  > ').strip()
        cmd = text.lower()
        if cmd == 'q':
            return 'quit'
        if cmd == 'h':
            message, clean = 'Hint: ' + puzzle['hint'], False
            continue
        if cmd == 's':
            finish(board, puzzle, solution, 'Solution: ')
            return 'shown'
        move = academy.parse_move(text)
        if not move:
            message = bad('Could not read that move. Example: D1 D8')
            continue
        src, dst, promo = move
        if (src, dst) not in board.legal_moves(chess.WHITE):
            message, clean = bad('That move is not legal here. Try again.'), False
            continue
        record = board.move_piece(board.get_spot(*src), board.get_spot(*dst), promo)
        mated = board.in_check(chess.BLACK) and not board.legal_moves(chess.BLACK)
        board.undo_move(record)
        if mated:
            finish(board, puzzle, move, 'Checkmate!  ')
            return 'star' if clean else 'solved'
        message, clean = bad('Legal, but not mate. Try again!'), False


def finish(board, puzzle, move, label):
    src, dst, promo = move
    board.move_piece(board.get_spot(*src), board.get_spot(*dst), promo)
    clear_screen()
    print(accent(f"  {puzzle['name']}"))
    print()
    academy.render_board(board, highlight=(src, dst), check=academy.king_in_check(board, chess.BLACK),
                         palette=WINTER)
    print()
    print('  ' + good(label) + bold(puzzle['san']))
    print('  ' + puzzle['explanation'])
    print()
    ask(dim('  [Enter] ring the next chime '))


def countdown(year):
    total, stars = len(NEW_YEAR_PUZZLES), 0
    for n, puzzle in enumerate(NEW_YEAR_PUZZLES, 1):
        result = countdown_puzzle(puzzle, n, total)
        if result == 'quit':
            return
        stars += result == 'star'
    fireworks(year)
    print()
    print('  ' + good(f'Midnight! You solved {stars} of {total} puzzles on the first try.'))
    print('  ' + dim('★' * stars + '☆' * (total - stars)))
    print()
    ask(dim('  [Enter] back to menu '))


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def snowy_game():
    game = chess.Game()
    # The game loop calls board.print_board(); draw the icy board instead.
    game.board.print_board = lambda: academy.render_board(
        game.board, check=academy.king_in_check(game.board, game.turn), palette=WINTER)
    game.play()


def winter_mode(today=None):
    year = new_year(today)
    snow_intro(year)
    while True:
        clear_screen()
        print(accent(f"  ❄  NEW YEAR'S EVE {year}"))
        print(dim('  Twelve chimes to midnight. Can you find every mate?'))
        print()
        print(f'  {bold("1")}. Countdown to Midnight   {dim(f"{len(NEW_YEAR_PUZZLES)} mate-in-1 puzzles, then fireworks")}')
        print(f'  {bold("2")}. Snowy game              {dim("play the computer on an icy board")}')
        print(f'  {bold("Q")}. Back')
        print()
        choice = ask('  > ').strip().lower()
        if choice == '1':
            countdown(year)
        elif choice == '2':
            snowy_game()
        elif choice in ('q', 'quit'):
            return


if __name__ == '__main__':
    winter_mode()
