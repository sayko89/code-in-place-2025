"""Render every image used in the README, in the "Chess Lab" visual style.

    assets/hero.png               Project hero (board position computed by the engine)
    assets/demo.gif               Fig. 2  Gameplay — Scholar's Mate
    assets/academy.gif            Fig. 4  Chess Academy — Légal's Mate with notes
    assets/terminal-play.png      Fig. 3  Real output of `python3 chess.py`
    assets/terminal-academy.png   Fig. 5  Real output of the Academy (ANSI colours)
    assets/certificate-plate.png  The Code in Place certificate (page 1 of assets/certificate.pdf)

Every chess position is produced by the game's own engine, and the two terminal
plates are rendered from the program's actual output — nothing is mocked up.

Requirements (only for regenerating images, not for playing): Pillow, and
`pdftoppm` (poppler) for the certificate plate.

    python3 tools/make_assets.py
"""
import os
import random
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
sys.path.insert(0, ROOT)

import chess  # noqa: E402
from academy import coord_move, play_line  # noqa: E402
from lessons import TRAPS  # noqa: E402

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
NAVY = (14, 20, 33)           # page
NAVY_2 = (21, 30, 47)         # panels
NAVY_3 = (34, 45, 66)         # hairlines on navy
IVORY = (243, 236, 221)
IVORY_DIM = (176, 170, 156)
MUTED = (122, 128, 142)
GOLD = (190, 160, 98)
GOLD_SOFT = (214, 190, 138)
RED = (176, 74, 62)

SQ_LIGHT = (233, 224, 203)    # board squares: ivory and bronze
SQ_DARK = (150, 125, 88)
HL = (214, 178, 96)           # last-move tint (blended)

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
DEJAVU = '/usr/share/fonts/truetype/dejavu/'


def font(name, size):
    path = os.path.join(FONTS, name)
    if not os.path.exists(path):  # fallback keeps the script usable without the bundled fonts
        path = DEJAVU + ('DejaVuSansMono.ttf' if 'Mono' in name else
                         'DejaVuSerif-Bold.ttf' if 'Playfair' in name else 'DejaVuSans.ttf')
    return ImageFont.truetype(path, size)


SERIF_BOLD = 'PlayfairDisplay-Bold.ttf'
SERIF_ITALIC = 'PlayfairDisplay-Italic.ttf'
SANS = 'IBMPlexSans-Regular.ttf'
SANS_SEMI = 'IBMPlexSans-SemiBold.ttf'
MONO = 'IBMPlexMono-Regular.ttf'
MONO_SEMI = 'IBMPlexMono-SemiBold.ttf'

SOLID = {chess.King: '♚', chess.Queen: '♛', chess.Rook: '♜',
         chess.Bishop: '♝', chess.Knight: '♞', chess.Pawn: '♟'}
OUTLINE = {chess.King: '♔', chess.Queen: '♕', chess.Rook: '♖',
           chess.Bishop: '♗', chess.Knight: '♘', chess.Pawn: '♙'}


def spaced(draw, xy, text, fnt, fill, tracking=0.0, anchor_right=False):
    """Draw text with letter-spacing (small caps style kicker lines)."""
    x, y = xy
    widths = [draw.textlength(ch, font=fnt) + tracking for ch in text]
    if anchor_right:
        x -= sum(widths) - tracking
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w
    return x


def wrap(draw, text, fnt, width):
    lines, line = [], ''
    for word in text.split():
        trial = (line + ' ' + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Board drawing
# ---------------------------------------------------------------------------

def draw_piece(img, piece, x, y, sq):
    pfont = ImageFont.truetype(DEJAVU + 'DejaVuSans.ttf', int(sq * 0.80))
    cls = type(piece)
    layer = Image.new('RGBA', (sq, sq), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = (sq / 2, sq / 2 + sq * 0.03)
    if piece.color == chess.WHITE:
        d.text(c, SOLID[cls], font=pfont, fill=(252, 249, 241), anchor='mm')
        d.text(c, OUTLINE[cls], font=pfont, fill=(24, 28, 38), anchor='mm')
    else:
        d.text(c, SOLID[cls], font=pfont, fill=(17, 22, 32), anchor='mm')
    alpha = layer.split()[3].filter(ImageFilter.GaussianBlur(sq / 26))
    shadow = Image.new('RGBA', (sq, sq), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.35)))
    img.alpha_composite(shadow, (int(x) + 1, int(y) + max(2, sq // 22)))
    img.alpha_composite(layer, (int(x), int(y)))


def draw_board(img, board, ox, oy, sq, last=(), check=None, moving=None, coords=True):
    """Board with a thin gold frame. moving = (piece, from_rc, to_rc, t)."""
    d = ImageDraw.Draw(img)
    size = sq * 8
    d.rectangle((ox - 12, oy - 12, ox + size + 11, oy + size + 11), outline=GOLD, width=1)
    for r in range(8):
        for c in range(8):
            x, y = ox + c * sq, oy + r * sq
            base = SQ_LIGHT if (r + c) % 2 == 0 else SQ_DARK
            if (r, c) in last:
                base = tuple(int(b * 0.45 + h * 0.55) for b, h in zip(base, HL))
            d.rectangle((x, y, x + sq - 1, y + sq - 1), fill=base)
    if check:
        x, y = ox + check[1] * sq, oy + check[0] * sq
        g = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((x + sq * .1, y + sq * .1, x + sq * .9, y + sq * .9), fill=RED + (235,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(sq / 8)))
        d = ImageDraw.Draw(img)
    if coords:
        cf = font(MONO, max(11, sq // 5))
        for i in range(8):
            d.text((ox + i * sq + sq / 2, oy + size + 26), chess.FILES[i].lower(), font=cf, fill=MUTED, anchor='mm')
            d.text((ox - 26, oy + i * sq + sq / 2), str(8 - i), font=cf, fill=MUTED, anchor='mm')
    skip = moving[1] if moving else None
    for r in range(8):
        for c in range(8):
            p = board.get_spot(r, c).piece
            if p and (r, c) != skip:
                draw_piece(img, p, ox + c * sq, oy + r * sq, sq)
    if moving:
        piece, (r0, c0), (r1, c1), t = moving
        e = t * t * (3 - 2 * t)
        draw_piece(img, piece, ox + (c0 + (c1 - c0) * e) * sq, oy + (r0 + (r1 - r0) * e) * sq, sq)


def king_square(board, color):
    if board.in_check(color):
        k = board.find_king(color)
        return (k.x, k.y)
    return None


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

def make_hero():
    W, H = 1280, 640
    img = Image.new('RGBA', (W, H), NAVY + (255,))
    d = ImageDraw.Draw(img)

    lx = 80
    spaced(d, (lx, 84), 'STANFORD CODE IN PLACE 2025  \u00b7  FINAL PROJECT', font(MONO_SEMI, 16), GOLD, tracking=2.0)
    d.line((lx, 120, lx + 56, 120), fill=GOLD, width=2)
    d.text((lx - 4, 138), 'Chess Lab', font=font(SERIF_BOLD, 118), fill=IVORY)
    d.text((lx, 292), 'A Study in Game Logic', font=font(SERIF_ITALIC, 44), fill=GOLD_SOFT)

    body = ('A complete chess engine and a small chess school for the terminal — '
            'written in pure Python and verified by tests.')
    y = 378
    for line in wrap(d, body, font(SANS, 23), 560):
        d.text((lx, y), line, font=font(SANS, 23), fill=IVORY_DIM)
        y += 36

    meta = 'Final project  ·  CS106A-based curriculum  ·  Safiye Özkan'
    d.line((lx, 532, lx + 560, 532), fill=NAVY_3, width=1)
    d.text((lx, 548), meta, font=font(MONO, 16), fill=MUTED)

    # Board: the final position of Légal's Mate, played out by the engine.
    legal = next(t for t in TRAPS if t['name'].startswith('Légal'))
    board, to_move, last = play_line(legal['moves'], len(legal['moves']))
    assert board.in_check(to_move) and not board.legal_moves(to_move)
    sq = 54
    ox, oy = W - 80 - sq * 8, 74
    draw_board(img, board, ox, oy, sq, last=set(last), check=king_square(board, to_move))
    d = ImageDraw.Draw(img)
    d.text((ox - 12, oy + sq * 8 + 46), 'Fig. 1', font=font(MONO_SEMI, 14), fill=GOLD)
    d.text((ox + 58, oy + sq * 8 + 43), 'Légal’s Mate, 7. Nd5# — computed by the engine',
           font=font(SERIF_ITALIC, 17), fill=IVORY_DIM)

    out = os.path.join(ASSETS, 'hero.png')
    img.convert('RGB').save(out, optimize=True)
    return out


# ---------------------------------------------------------------------------
# Animated figures
# ---------------------------------------------------------------------------

def make_gif(lesson, out, fig, title, labels, intro, banner, notes):
    sq = 60
    pad_x, top = 52, 86
    note_h = 34 if notes else 0
    W = pad_x * 2 + sq * 8
    H = top + sq * 8 + 66 + note_h + 40
    frames, durations = [], []

    def frame(board, last=(), check=None, status='', status_color=IVORY, note='', moving=None, plate=None):
        img = Image.new('RGBA', (W, H), NAVY + (255,))
        d = ImageDraw.Draw(img)
        spaced(d, (pad_x - 12, 30), f'CHESS LAB  ·  FIG. {fig}', font(MONO_SEMI, 13), GOLD, tracking=1.6)
        d.text((W - pad_x + 12, 26), title, font=font(SERIF_ITALIC, 19), fill=IVORY_DIM, anchor='ra')
        draw_board(img, board, pad_x, top, sq, last=last, check=check, moving=moving)
        d = ImageDraw.Draw(img)
        sy = top + sq * 8 + 50
        d.text((pad_x - 12, sy), '›', font=font(MONO_SEMI, 18), fill=GOLD)
        d.text((pad_x + 6, sy), status, font=font(MONO_SEMI, 17), fill=status_color)
        if notes and note:
            for i, line in enumerate(wrap(d, note, font(SANS, 15), W - 2 * pad_x)[:2]):
                d.text((pad_x + 6, sy + 30 + i * 20), line, font=font(SANS, 15), fill=IVORY_DIM)
        if plate:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            od.rectangle((pad_x, top, pad_x + sq * 8, top + sq * 8), fill=NAVY + (120,))
            cy = top + sq * 4
            od.rectangle((pad_x + 56, cy - 62, pad_x + sq * 8 - 56, cy + 62), fill=NAVY + (242,))
            od.rectangle((pad_x + 64, cy - 54, pad_x + sq * 8 - 64, cy + 54), outline=GOLD + (255,), width=1)
            img.alpha_composite(ov)
            d = ImageDraw.Draw(img)
            d.text((W / 2, cy - 14), plate[0], font=font(SERIF_BOLD, 40), fill=IVORY, anchor='mm')
            d.text((W / 2, cy + 28), plate[1], font=font(SERIF_ITALIC, 18), fill=GOLD_SOFT, anchor='mm')
        return img.convert('RGB')

    def add(f, ms):
        frames.append(f)
        durations.append(ms)

    board = chess.Board()
    add(frame(board, status=intro), 1300)
    turn, last = chess.WHITE, ()
    for n, (coord, san, comment) in enumerate(lesson['moves']):
        s, e, promo = coord_move(coord)
        assert (s, e) in board.legal_moves(turn), san
        piece = board.get_spot(*s).piece
        number = f'{n // 2 + 1}.' if n % 2 == 0 else f'{n // 2 + 1}...'
        label = f'{labels[n % 2]}{number} {san}'
        for i in range(1, 9):
            add(frame(board, last=last, status=label, note=comment, moving=(piece, s, e, i / 8)), 40)
        board.move_piece(board.get_spot(*s), board.get_spot(*e), promo)
        last = {s, e}
        turn = chess.opponent(turn)
        check = king_square(board, turn)
        add(frame(board, last=last, check=check, status=label, note=comment,
                  status_color=RED if check else IVORY), 1700 if notes and comment else 650)

    assert board.in_check(turn) and not board.legal_moves(turn)
    check = king_square(board, turn)
    final = 'Checkmate. ' + ('Black' if turn == chess.BLACK else 'White') + ' is mated.'
    add(frame(board, last=last, check=check, status=final, status_color=RED), 900)
    add(frame(board, last=last, check=check, status=final, status_color=RED, plate=banner), 3400)

    pal = [f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durations, loop=0, optimize=True, disposal=1)
    return out


# ---------------------------------------------------------------------------
# Terminal plates (real program output)
# ---------------------------------------------------------------------------

def xterm256(n):
    base = [(0, 0, 0), (205, 0, 0), (0, 205, 0), (205, 205, 0), (0, 0, 238), (205, 0, 205),
            (0, 205, 205), (229, 229, 229), (127, 127, 127), (255, 0, 0), (0, 255, 0),
            (255, 255, 0), (92, 92, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
    if n < 16:
        return base[n]
    if n < 232:
        n -= 16
        steps = [0, 95, 135, 175, 215, 255]
        return steps[n // 36], steps[(n // 6) % 6], steps[n % 6]
    v = 8 + (n - 232) * 10
    return v, v, v


# The plate uses a terminal theme in the project's colours for the 16 basic colours.
THEME = {31: RED, 32: (143, 176, 128), 33: GOLD_SOFT, 36: GOLD_SOFT}


def parse_ansi(text):
    """Yield lines of (char, fg, bg, bold, dim) cells."""
    lines, cells = [], []
    fg, bg, bold, dim = None, None, False, False
    for token in re.split(r'(\x1b\[[0-9;]*m)', text):
        if token.startswith('\x1b['):
            codes = [int(c) for c in token[2:-1].split(';') if c] or [0]
            i = 0
            while i < len(codes):
                c = codes[i]
                if c == 0:
                    fg, bg, bold, dim = None, None, False, False
                elif c == 1:
                    bold = True
                elif c == 2:
                    dim = True
                elif c in THEME:
                    fg = THEME[c]
                elif c in (38, 48) and i + 2 < len(codes) and codes[i + 1] == 5:
                    if c == 38:
                        fg = xterm256(codes[i + 2])
                    else:
                        bg = xterm256(codes[i + 2])
                    i += 2
                i += 1
            continue
        for ch in token:
            if ch == '\n':
                lines.append(cells)
                cells = []
            elif ch != '\r':
                cells.append((ch, fg, bg, bold, dim))
    lines.append(cells)
    return lines


def make_terminal_plate(text, out, fig, caption, command):
    lines = parse_ansi(text)
    while lines and not lines[-1]:
        lines.pop()
    cw, lh, fs = 11, 22, 18
    regular, bold_f = font(MONO, fs), font(MONO_SEMI, fs)
    glyph_f = ImageFont.truetype(DEJAVU + 'DejaVuSansMono.ttf', fs)
    cols = max(len(line) for line in lines)
    pad, bar = 30, 46
    win_w = max(cols * cw + pad * 2, 700)
    win_h = bar + len(lines) * lh + pad * 2
    W, H = win_w + 120, win_h + 140
    img = Image.new('RGBA', (W, H), NAVY + (255,))
    d = ImageDraw.Draw(img)
    spaced(d, (60, 30), f'CHESS LAB  ·  FIG. {fig}', font(MONO_SEMI, 13), GOLD, tracking=1.6)
    d.text((W - 60, 26), caption, font=font(SERIF_ITALIC, 19), fill=IVORY_DIM, anchor='ra')
    wx, wy = 60, 70
    d.rectangle((wx, wy, wx + win_w, wy + win_h), fill=NAVY_2, outline=NAVY_3)
    d.line((wx, wy + bar, wx + win_w, wy + bar), fill=NAVY_3)
    d.text((wx + 22, wy + 14), command, font=font(MONO, 15), fill=MUTED)
    for r, cells in enumerate(lines):
        y = wy + bar + pad + r * lh
        for c, (ch, fg, bg, bold, dim) in enumerate(cells):
            x = wx + pad + c * cw
            if bg:
                d.rectangle((x, y - 2, x + cw, y + lh - 2), fill=bg)
            color = fg or IVORY
            if dim and not fg:
                color = MUTED
            f = glyph_f if '♔' <= ch <= '♟' else (bold_f if bold else regular)
            if ch.strip():
                d.text((x + cw / 2, y + lh / 2 - 2), ch, font=f, fill=color, anchor='mm')
    img.convert('RGB').save(out, optimize=True)
    return out


def capture_play_session():
    """Run a real game with scripted input and return the program's output."""
    keys = 'G1 F3\nE2 E3\nF1 E2\nO-O\nQ\nQ\n'
    code = ('import random, chess; random.seed(3); chess.main_menu()')
    result = subprocess.run([sys.executable, '-c', code], input='1\n' + keys, cwd=ROOT,
                            capture_output=True, text=True, env={**os.environ, 'NO_COLOR': '1'})
    out = result.stdout
    # The prompts are printed without the typed answer (stdin is a pipe); put the answers back.
    answers = iter(keys.split('\n'))
    out = re.sub(r'(Your move \(e\.g\. E2 E4, O-O, or Q to quit\): )',
                 lambda m: m.group(1) + next(answers) + '\n', out)
    # Show the end of the session: the board after White castles.
    lines = out.split('\n')
    end = max(i for i, l in enumerate(lines) if 'castles king side' in l)
    start = max(i for i in range(end) if lines[i].startswith('8 ')) - 0
    return '\n'.join(lines[start:end + 1])


def capture_academy_screen():
    """Run the Academy in a pseudo-terminal (so it uses colours) and grab the last screen
    of Légal's Mate."""
    keys = '2\n3\n' + '\n' * 13
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, 'run.py')
        with open(script, 'w') as f:
            f.write('import pty, os, sys\n'
                    f'os.chdir({ROOT!r})\n'
                    'pid, fd = pty.fork()\n'
                    'if pid == 0:\n'
                    f'    os.execvp({sys.executable!r}, [{sys.executable!r}, "-c", "import academy; academy.academy()"])\n'
                    'import time\n'
                    f'keys = {keys!r}\n'
                    'out = b""\n'
                    'time.sleep(0.4)\n'
                    'for k in keys:\n'
                    '    os.write(fd, k.encode()); time.sleep(0.12)\n'
                    '    try:\n'
                    '        import select\n'
                    '        while select.select([fd], [], [], 0.05)[0]:\n'
                    '            out += os.read(fd, 65536)\n'
                    '    except OSError:\n'
                    '        break\n'
                    'sys.stdout.buffer.write(out)\n'
                    'os.kill(pid, 9)\n')
        raw = subprocess.run([sys.executable, script], capture_output=True).stdout.decode('utf-8', 'replace')
    screen = raw.split('\x1b[2J\x1b[H')[-1]
    screen = screen.split('move 13/13')[0].rstrip()
    screen = re.sub(r'\n[^\n]*$', '', screen) if screen.endswith('\x1b[0m') is False else screen
    return screen.replace('\r', '')


def make_certificate_plate():
    pdf = os.path.join(ASSETS, 'certificate.pdf')
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', '110', '-png', '-f', '1', '-l', '1', pdf,
                        os.path.join(tmp, 'p')], check=True)
        page = Image.open(next(os.path.join(tmp, f) for f in os.listdir(tmp))).convert('RGB')
    target_h = 560
    page = page.resize((int(page.width * target_h / page.height), target_h), Image.LANCZOS)
    W, H = 1280, target_h + 160
    img = Image.new('RGBA', (W, H), NAVY + (255,))
    px, py = 80, 80
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((px + 8, py + 14, px + page.width + 8, py + target_h + 14), fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    img.paste(page, (px, py))
    d = ImageDraw.Draw(img)
    d.rectangle((px - 12, py - 12, px + page.width + 11, py + target_h + 11), outline=GOLD, width=1)

    tx = px + page.width + 80
    spaced(d, (tx, py + 6), 'CERTIFICATE OF COMPLETION', font(MONO_SEMI, 15), GOLD, tracking=2)
    d.text((tx - 2, py + 40), 'Code in Place', font=font(SERIF_BOLD, 58), fill=IVORY)
    d.text((tx, py + 118), 'Stanford University · 2025', font=font(SERIF_ITALIC, 28), fill=GOLD_SOFT)
    facts = [('Dates', 'April 21 – June 6, 2025'),
             ('Curriculum', "Material from Stanford's CS106A"),
             ('Language', 'Python'),
             ('Badges', 'Diagnostic  ·  Final Project'),
             ('Awarded to', 'Safiye Özkan')]
    y = py + 196
    for k, v in facts:
        d.line((tx, y, W - 80, y), fill=NAVY_3)
        d.text((tx, y + 14), k.upper(), font=font(MONO, 13), fill=MUTED)
        d.text((tx + 150, y + 10), v, font=font(SANS, 20), fill=IVORY)
        y += 54
    d.line((tx, y, W - 80, y), fill=NAVY_3)
    d.text((tx, y + 22), 'Details transcribed from the certificate PDF in this repository.',
           font=font(SERIF_ITALIC, 16), fill=MUTED)
    out = os.path.join(ASSETS, 'certificate-plate.png')
    img.convert('RGB').save(out, optimize=True)
    return out


def main():
    os.makedirs(ASSETS, exist_ok=True)
    traps = {t['name']: t for t in TRAPS}
    outputs = [
        make_hero(),
        make_gif(traps["Scholar's Mate"], os.path.join(ASSETS, 'demo.gif'), 2, 'Gameplay — Scholar’s Mate',
                 labels=('White  ', 'Computer  '), intro='python3 chess.py',
                 banner=('Checkmate.', 'Scholar’s Mate · 4. Qxf7#'), notes=False),
        make_terminal_plate(capture_play_session(), os.path.join(ASSETS, 'terminal-play.png'), 3,
                            'Real output — White castles', '~/code-in-place-2025 — python3 chess.py'),
        make_gif(traps["Légal's Mate"], os.path.join(ASSETS, 'academy.gif'), 4,
                 'Chess Academy — Légal’s Mate', labels=('', ''),
                 intro='Academy › Traps › Légal’s Mate',
                 banner=('Checkmate.', 'Légal’s Mate · 7. Nd5#'), notes=True),
        make_terminal_plate(capture_academy_screen(), os.path.join(ASSETS, 'terminal-academy.png'), 5,
                            'Real output — the Academy in colour', '~/code-in-place-2025 — Chess Academy'),
        make_certificate_plate(),
    ]
    for path in outputs:
        print(f'wrote {os.path.relpath(path, ROOT)}  ({os.path.getsize(path) // 1024} KB)')


if __name__ == '__main__':
    main()
