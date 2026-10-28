"""Render an animated demo of the game (Scholar's Mate) to assets/demo.gif.

Every move is validated with the game's own engine in chess.py, so the
animation only shows moves the program itself accepts.

Usage:  python3 tools/make_demo_gif.py      (requires Pillow)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import chess  # noqa: E402

# --- Look & feel -------------------------------------------------------------
SQ = 64                       # square size in px
PAD = 36                      # frame around the board (for coordinates)
HEADER = 48                   # title bar height
FOOTER = 52                   # status bar height
W = PAD * 2 + SQ * 8
H = HEADER + PAD * 2 + SQ * 8 + FOOTER

BG = (22, 27, 34)             # GitHub dark
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HL_LIGHT = (246, 236, 140)    # last-move highlight
HL_DARK = (218, 195, 92)
CHECK = (231, 76, 60)
TEXT = (230, 237, 243)
MUTED = (139, 148, 158)
ACCENT = (88, 166, 255)

FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
PIECE_FONT = ImageFont.truetype(FONT_DIR + 'DejaVuSans.ttf', int(SQ * 0.82))
TITLE_FONT = ImageFont.truetype(FONT_DIR + 'DejaVuSans-Bold.ttf', 22)
SUB_FONT = ImageFont.truetype(FONT_DIR + 'DejaVuSans.ttf', 13)
COORD_FONT = ImageFont.truetype(FONT_DIR + 'DejaVuSans-Bold.ttf', 13)
STATUS_FONT = ImageFont.truetype(FONT_DIR + 'DejaVuSansMono-Bold.ttf', 17)

# Solid glyphs are used as the body, outline glyphs as the edge.
SOLID = {chess.King: '♚', chess.Queen: '♛', chess.Rook: '♜',
         chess.Bishop: '♝', chess.Knight: '♞', chess.Pawn: '♟'}
OUTLINE = {chess.King: '♔', chess.Queen: '♕', chess.Rook: '♖',
           chess.Bishop: '♗', chess.Knight: '♘', chess.Pawn: '♙'}

MOVES = [('E2', 'E4'), ('E7', 'E5'),
         ('F1', 'C4'), ('B8', 'C6'),
         ('D1', 'H5'), ('G8', 'F6'),
         ('H5', 'F7')]
SAN = ['e4', 'e5', 'Bc4', 'Nc6', 'Qh5', 'Nf6??', 'Qxf7#']


def square_xy(row, col):
    return PAD + col * SQ, HEADER + PAD + row * SQ


def draw_piece(img, piece, x, y):
    cls = type(piece)
    layer = Image.new('RGBA', (SQ, SQ), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = SQ / 2, SQ / 2 + 2
    if piece.color == chess.WHITE:
        d.text((cx, cy), SOLID[cls], font=PIECE_FONT, fill=(250, 248, 240), anchor='mm')
        d.text((cx, cy), OUTLINE[cls], font=PIECE_FONT, fill=(30, 30, 30), anchor='mm')
    else:
        d.text((cx, cy), SOLID[cls], font=PIECE_FONT, fill=(32, 32, 36), anchor='mm')
    # soft drop shadow
    alpha = layer.split()[3].filter(ImageFilter.GaussianBlur(2.5))
    shadow = Image.new('RGBA', (SQ, SQ), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.45)))
    img.alpha_composite(shadow, (int(x) + 2, int(y) + 3))
    img.alpha_composite(layer, (int(x), int(y)))


def render(board, last=None, check_sq=None, status='', status_color=TEXT,
           moving=None, banner=None):
    """moving = (piece, from_rc, to_rc, t) draws a piece mid-flight."""
    img = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    # Header
    d.text((PAD, 14), '♞  Terminal Chess', font=TITLE_FONT, fill=TEXT)
    d.text((W - PAD, 22), 'Python · OOP · Code in Place 2025',
           font=SUB_FONT, fill=MUTED, anchor='ra')

    # Board shadow + frame
    bx, by = PAD, HEADER + PAD
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        (bx - 6, by - 6, bx + SQ * 8 + 6, by + SQ * 8 + 6), 10, fill=(0, 0, 0, 160))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((bx - 6, by - 6, bx + SQ * 8 + 6, by + SQ * 8 + 6), 8, fill=(48, 36, 28))

    # Squares
    for r in range(8):
        for c in range(8):
            x, y = square_xy(r, c)
            light = (r + c) % 2 == 0
            color = LIGHT if light else DARK
            if last and (r, c) in last:
                color = HL_LIGHT if light else HL_DARK
            d.rectangle((x, y, x + SQ - 1, y + SQ - 1), fill=color)

    # Check glow under the king
    if check_sq:
        x, y = square_xy(*check_sq)
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((x + 4, y + 4, x + SQ - 4, y + SQ - 4), fill=CHECK + (230,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(7)))
        d = ImageDraw.Draw(img)

    # Coordinates
    for i in range(8):
        d.text((bx + i * SQ + SQ / 2, by + SQ * 8 + 18), chess.FILES[i],
               font=COORD_FONT, fill=MUTED, anchor='mm')
        d.text((bx - 20, by + i * SQ + SQ / 2), str(8 - i),
               font=COORD_FONT, fill=MUTED, anchor='mm')

    # Pieces
    skip = moving[1] if moving else None
    for r in range(8):
        for c in range(8):
            p = board.get_spot(r, c).piece
            if p and (r, c) != skip:
                draw_piece(img, p, *square_xy(r, c))
    if moving:
        piece, (r0, c0), (r1, c1), t = moving
        e = t * t * (3 - 2 * t)  # smoothstep easing
        x0, y0 = square_xy(r0, c0)
        x1, y1 = square_xy(r1, c1)
        draw_piece(img, piece, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)

    # Status bar
    d = ImageDraw.Draw(img)
    sy = HEADER + PAD * 2 + SQ * 8 + 4
    d.text((PAD, sy + 10), '$', font=STATUS_FONT, fill=ACCENT)
    d.text((PAD + 20, sy + 10), status, font=STATUS_FONT, fill=status_color)

    # Final banner
    if banner:
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle((bx, by, bx + SQ * 8, by + SQ * 8), fill=(10, 12, 16, 110))
        cy = by + SQ * 4
        od.rounded_rectangle((bx + 40, cy - 52, bx + SQ * 8 - 40, cy + 52), 14,
                             fill=(22, 27, 34, 235), outline=CHECK + (255,), width=3)
        img.alpha_composite(ov)
        d = ImageDraw.Draw(img)
        big = ImageFont.truetype(FONT_DIR + 'DejaVuSans-Bold.ttf', 34)
        d.text((W / 2, cy - 12), banner[0], font=big, fill=TEXT, anchor='mm')
        d.text((W / 2, cy + 26), banner[1], font=SUB_FONT, fill=MUTED, anchor='mm')

    return img.convert('RGB')


def main():
    game = chess.Game()
    board = game.board
    frames, durations = [], []

    def add(frame, ms):
        frames.append(frame)
        durations.append(ms)

    add(render(board, status='python3 chess.py'), 1200)

    last = None
    turn = chess.WHITE
    for n, ((src, dst), san) in enumerate(zip(MOVES, SAN)):
        s, e = game.parse_input(f'{src} {dst}')
        assert (s, e) in board.legal_moves(turn), f'illegal move {src} {dst}'
        piece = board.get_spot(*s).piece
        who = 'White' if turn == chess.WHITE else 'Computer'
        prompt = f'{n // 2 + 1}. {"" if turn == chess.WHITE else "... "}{san}'
        label = f'{who}: {src} {dst}   ({prompt})'

        steps = 8
        for i in range(1, steps + 1):
            add(render(board, last=last, status=label, moving=(piece, s, e, i / steps)), 40)
        board.move_piece(board.get_spot(*s), board.get_spot(*e))
        last = {s, e}
        turn = chess.opponent(turn)

        check_sq = None
        status, color = label, TEXT
        if board.in_check(turn):
            k = board.find_king(turn)
            check_sq = (k.x, k.y)
            status, color = label + '   Check!', CHECK
        add(render(board, last=last, check_sq=check_sq, status=status, status_color=color), 650)

    # Engine confirms: Black is in check with no legal moves.
    assert board.in_check(chess.BLACK) and not board.legal_moves(chess.BLACK)
    k = board.find_king(chess.BLACK)
    final = 'Checkmate! Black is mated — White wins.'
    add(render(board, last=last, check_sq=(k.x, k.y), status=final, status_color=CHECK), 900)
    add(render(board, last=last, check_sq=(k.x, k.y), status=final, status_color=CHECK,
               banner=('CHECKMATE', "Scholar's Mate · 4. Qxf7#")), 3200)

    out = os.path.join(ROOT, 'assets', 'demo.gif')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pal = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
           for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durations,
                loop=0, optimize=True, disposal=1)
    print(f'wrote {out} ({len(frames)} frames, {os.path.getsize(out) // 1024} KB)')


if __name__ == '__main__':
    main()
