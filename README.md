# ♟️ Terminal Chess — Code in Place 2025 Final Project

A terminal-based chess game written in Python, built as my final project for
[Stanford's Code in Place 2025](https://codeinplace.stanford.edu/) (based on CS106A).
You play White against a computer opponent that picks a random legal move.

🎓 **Verified certificate:** [View on Code in Place](https://codeinplace.stanford.edu/cip5/certificate/pj0y0n)

---

## Demo

```
8 r n b q k b n r
7 p p p p p p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . P . . .
3 . . . . . . . .
2 P P P P . P P P
1 R N B Q K B N R
  A B C D E F G H
Turn: Black
Computer played: G8 to F6
```

Uppercase letters are White pieces, lowercase are Black (`K` king, `Q` queen,
`R` rook, `B` bishop, `N` knight, `P` pawn).

## How to run

Requires Python 3 — no external libraries.

```bash
git clone https://github.com/sayko89/code-in-place-2025.git
cd code-in-place-2025
python3 chess.py
```

Enter moves as `<from> <to>`, e.g. `E2 E4`. Type `Q` to quit.

## Features

- Movement rules for all six piece types, including pawn double-step from the starting rank
- Path checking so sliding pieces (rook, bishop, queen) can't jump over others
- **Check, checkmate and stalemate detection** — moves that would leave your own king in check are rejected (including pinned pieces)
- Human (White) vs. computer (Black), turn by turn
- Input validation with a retry prompt on invalid moves
- Board redrawn after every move

## Design

The code is organized around a small object-oriented model:

| Class | Responsibility |
|-------|----------------|
| `Spot` | One square on the board and the piece on it |
| `Piece` | Base class; each subclass (`King`, `Queen`, `Rook`, `Bishop`, `Knight`, `Pawn`) implements its own `can_move` |
| `Board` | 8×8 grid, setup, path checking, legal move generation (each candidate move is played, checked for king safety, then undone) |
| `Game` | Input parsing and the main game loop |

## Limitations & next steps

This is a learning project, so some rules aren't implemented yet:

- [x] Check, checkmate and stalemate detection
- [ ] Castling, en passant and pawn promotion
- [ ] A smarter opponent (e.g. minimax with material evaluation instead of random moves)
- [ ] Unit tests for piece movement

## Built with

Python 3 · Object-oriented design · CLI
