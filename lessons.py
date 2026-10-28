"""Content for the Chess Academy: openings, traps, puzzles and tips.

Moves are written as "<from><to>" (e.g. "e2e4") together with their standard
algebraic notation (SAN) and a short explanation. Every line here is checked
against the game engine by `tests/test_lessons.py`.
"""

# ---------------------------------------------------------------------------
# Openings
# ---------------------------------------------------------------------------
OPENINGS = [
    {
        'name': 'Italian Game',
        'summary': 'One of the oldest openings. White develops fast and aims the bishop at f7, '
                   "Black's weakest square.",
        'moves': [
            ('e2e4', 'e4', 'White grabs the center and opens lines for the queen and bishop.'),
            ('e7e5', 'e5', 'Black claims an equal share of the center.'),
            ('g1f3', 'Nf3', 'The knight develops and immediately attacks the e5 pawn.'),
            ('b8c6', 'Nc6', 'Black defends e5 while developing a piece.'),
            ('f1c4', 'Bc4', 'The "Italian" bishop eyes f7, defended only by the king.'),
            ('f8c5', 'Bc5', 'Giuoco Piano ("quiet game"): Black mirrors White.'),
            ('c2c3', 'c3', 'White prepares d4 to build a big pawn center.'),
            ('g8f6', 'Nf6', 'Black develops and counter-attacks e4.'),
            ('d2d3', 'd3', 'A solid modern choice: e4 is protected, the fight is slow.'),
            ('d7d6', 'd6', 'Both sides are ready to castle. A classic, balanced position.'),
        ],
    },
    {
        'name': 'Ruy Lopez (Spanish Opening)',
        'summary': 'A favorite of world champions. White pressures the knight that defends e5.',
        'moves': [
            ('e2e4', 'e4', 'Center control.'),
            ('e7e5', 'e5', 'Black answers symmetrically.'),
            ('g1f3', 'Nf3', 'Attacking e5.'),
            ('b8c6', 'Nc6', 'Defending e5.'),
            ('f1b5', 'Bb5', 'The Spanish bishop attacks the knight that defends e5.'),
            ('a7a6', 'a6', 'The Morphy Defence: "Bishop, make up your mind!"'),
            ('b5a4', 'Ba4', 'White keeps the pressure instead of trading.'),
            ('g8f6', 'Nf6', 'Black develops and hits e4. This is the main line.'),
        ],
    },
    {
        'name': 'Sicilian Defence — Najdorf',
        'summary': "Black's most combative reply to 1.e4. The position is unbalanced from move one.",
        'moves': [
            ('e2e4', 'e4', 'White takes the center.'),
            ('c7c5', 'c5', 'Black fights for d4 from the side instead of copying White.'),
            ('g1f3', 'Nf3', 'Preparing d4.'),
            ('d7d6', 'd6', 'Controls e5 and opens the light-squared bishop.'),
            ('d2d4', 'd4', 'White opens the center.'),
            ('c5d4', 'cxd4', 'Black trades a wing pawn for a center pawn — a good deal.'),
            ('f3d4', 'Nxd4', 'White recaptures with a strong central knight.'),
            ('g8f6', 'Nf6', 'Attacks e4 with tempo.'),
            ('b1c3', 'Nc3', 'Defends e4.'),
            ('a7a6', 'a6', 'The Najdorf! Keeps White pieces off b5 and prepares ...e5 or ...b5.'),
        ],
    },
    {
        'name': 'French Defence',
        'summary': 'A solid defence. Black builds a pawn chain and counter-attacks the center.',
        'moves': [
            ('e2e4', 'e4', 'Center.'),
            ('e7e6', 'e6', 'Preparing ...d5 with full support.'),
            ('d2d4', 'd4', 'White builds an ideal center.'),
            ('d7d5', 'd5', 'Black immediately challenges e4.'),
            ('b1c3', 'Nc3', 'White defends e4 with a piece.'),
            ('g8f6', 'Nf6', 'More pressure on e4.'),
            ('c1g5', 'Bg5', 'Pins the knight that attacks e4.'),
            ('f8e7', 'Be7', 'Black breaks the pin calmly. The Classical French.'),
        ],
    },
    {
        'name': 'Caro-Kann Defence',
        'summary': 'Like the French, but the light-squared bishop gets out before ...e6.',
        'moves': [
            ('e2e4', 'e4', 'Center.'),
            ('c7c6', 'c6', 'Preparing ...d5.'),
            ('d2d4', 'd4', 'White takes the full center.'),
            ('d7d5', 'd5', 'Challenge!'),
            ('b1c3', 'Nc3', 'Defending e4.'),
            ('d5e4', 'dxe4', 'Black releases the tension.'),
            ('c3e4', 'Nxe4', 'White recaptures with a well-placed knight.'),
            ('c8f5', 'Bf5', "The point of the Caro-Kann: the bishop is active, not stuck behind e6."),
        ],
    },
    {
        'name': "Queen's Gambit Declined",
        'summary': "White offers a pawn for the center; Black politely declines and stays solid.",
        'moves': [
            ('d2d4', 'd4', 'A queen-pawn opening.'),
            ('d7d5', 'd5', 'Black stops e4.'),
            ('c2c4', 'c4', "The Queen's Gambit: a wing pawn for Black's center pawn."),
            ('e7e6', 'e6', 'Declined — Black keeps a pawn on d5.'),
            ('b1c3', 'Nc3', 'More pressure on d5.'),
            ('g8f6', 'Nf6', 'Defends d5.'),
            ('c1g5', 'Bg5', "Pins the knight — the queen on d8 is behind it."),
            ('f8e7', 'Be7', 'Breaks the pin. The Orthodox Defence.'),
        ],
    },
    {
        'name': "King's Indian Defence",
        'summary': 'Black lets White build a big center, then attacks it later.',
        'moves': [
            ('d2d4', 'd4', 'Center.'),
            ('g8f6', 'Nf6', 'Flexible: stops e4 for now.'),
            ('c2c4', 'c4', 'More space.'),
            ('g7g6', 'g6', 'Preparing a fianchetto.'),
            ('b1c3', 'Nc3', 'Supporting e4.'),
            ('f8g7', 'Bg7', 'The bishop aims down the long diagonal at the center.'),
            ('e2e4', 'e4', 'White builds a huge center.'),
            ('d7d6', 'd6', 'Black prepares ...e5 to strike back. Sharp play ahead!'),
        ],
    },
    {
        'name': 'London System',
        'summary': 'A simple, reliable setup for White that works against almost anything.',
        'moves': [
            ('d2d4', 'd4', 'Center.'),
            ('d7d5', 'd5', 'Black mirrors.'),
            ('c1f4', 'Bf4', 'The London bishop comes out before e3 locks it in.'),
            ('g8f6', 'Nf6', 'Development.'),
            ('e2e3', 'e3', 'Solid pawn triangle: d4, e3, and soon c3.'),
            ('e7e6', 'e6', 'Black opens the dark-squared bishop.'),
            ('g1f3', 'Nf3', 'Development.'),
            ('c7c5', 'c5', 'Black challenges the center.'),
            ('c2c3', 'c3', 'White completes the pyramid. Easy to learn, hard to crack.'),
            ('b8c6', 'Nc6', 'Black develops. Both sides have a comfortable game.'),
        ],
    },
]

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------
TRAPS = [
    {
        'name': "Fool's Mate",
        'summary': 'The fastest checkmate possible — 2 moves. Lesson: never weaken the e1–h4 diagonal.',
        'moves': [
            ('f2f3', 'f3', 'A weakening move: the king loses a defender.'),
            ('e7e5', 'e5', 'Black opens the queen.'),
            ('g2g4', 'g4??', 'The losing blunder. The diagonal to e1 is now wide open.'),
            ('d8h4', 'Qh4#', 'Checkmate in two moves!'),
        ],
    },
    {
        'name': "Scholar's Mate",
        'summary': 'Queen and bishop attack f7 together. Very common in beginner games.',
        'moves': [
            ('e2e4', 'e4', 'Normal start.'),
            ('e7e5', 'e5', 'Normal reply.'),
            ('f1c4', 'Bc4', 'The bishop aims at f7.'),
            ('b8c6', 'Nc6', 'Natural development.'),
            ('d1h5', 'Qh5', 'Second attacker on f7 (and on e5).'),
            ('g8f6', 'Nf6??', 'Attacks the queen but ignores the threat. ...g6 or ...Qe7 was needed.'),
            ('h5f7', 'Qxf7#', 'The queen takes f7, protected by the bishop. Checkmate.'),
        ],
    },
    {
        'name': "Légal's Mate",
        'summary': 'White sacrifices the queen and mates with minor pieces. A famous 18th-century trap.',
        'moves': [
            ('e2e4', 'e4', ''),
            ('e7e5', 'e5', ''),
            ('g1f3', 'Nf3', ''),
            ('d7d6', 'd6', 'The Philidor Defence.'),
            ('f1c4', 'Bc4', 'The bishop eyes f7.'),
            ('c8g4', 'Bg4', 'Pins the knight to the queen.'),
            ('b1c3', 'Nc3', 'White develops and sets the trap.'),
            ('g7g6', 'g6?', 'Too slow — Black does not see the danger.'),
            ('f3e5', 'Nxe5!!', 'Ignoring the pin! The queen is offered.'),
            ('g4d1', 'Bxd1??', 'Greedy. ...dxe5 would lose only a pawn.'),
            ('c4f7', 'Bxf7+', 'Check!'),
            ('e8e7', 'Ke7', 'Forced — the only move.'),
            ('c3d5', 'Nd5#', 'Three minor pieces checkmate the king. Material does not matter!'),
        ],
    },
    {
        'name': 'Blackburne Shilling Trap',
        'summary': 'Black lets White win a pawn — and then traps the king.',
        'moves': [
            ('e2e4', 'e4', ''),
            ('e7e5', 'e5', ''),
            ('g1f3', 'Nf3', ''),
            ('b8c6', 'Nc6', ''),
            ('f1c4', 'Bc4', ''),
            ('c6d4', 'Nd4?!', 'A dubious move that sets a trap. The e5 pawn looks free.'),
            ('f3e5', 'Nxe5?', 'White takes the bait.'),
            ('d8g5', 'Qg5!', 'Attacks the knight AND the g2 pawn.'),
            ('e5f7', 'Nxf7??', 'Forking queen and rook... but it is too late.'),
            ('g5g2', 'Qxg2', 'Attacks the rook on h1.'),
            ('h1f1', 'Rf1', 'Saving the rook.'),
            ('g2e4', 'Qxe4+', 'Check — the e-file opens.'),
            ('c4e2', 'Be2', 'The only block... and the bishop is now pinned.'),
            ('d4f3', 'Nf3#', 'A smothered-style checkmate. The bishop cannot take because it is pinned.'),
        ],
    },
    {
        'name': 'Englund Gambit Trap',
        'summary': 'A trap against 1.d4. The queen sneaks all the way to c1.',
        'moves': [
            ('d2d4', 'd4', ''),
            ('e7e5', 'e5?!', 'The Englund Gambit — a risky pawn sacrifice.'),
            ('d4e5', 'dxe5', 'White accepts.'),
            ('b8c6', 'Nc6', 'Attacks e5.'),
            ('g1f3', 'Nf3', 'Defends e5.'),
            ('d8e7', 'Qe7', 'Attacks e5 a third time.'),
            ('c1f4', 'Bf4', 'Defends e5 again.'),
            ('e7b4', 'Qb4+', 'Surprise! Check, and b2 is attacked.'),
            ('f4d2', 'Bd2', 'Natural block.'),
            ('b4b2', 'Qxb2', 'Now the rook on a1 is attacked.'),
            ('d2c3', 'Bc3?', 'Looks active...'),
            ('f8b4', 'Bb4!', 'Pins the bishop to the king.'),
            ('d1d2', 'Qd2', 'Trying to break the pin.'),
            ('b4c3', 'Bxc3', ''),
            ('d2c3', 'Qxc3', ''),
            ('b2c1', 'Qc1#', 'Back-rank checkmate! The d1 square is empty and nothing can block.'),
        ],
    },
    {
        'name': 'Elephant Trap',
        'summary': 'White grabs a "free" pawn on d5 and loses a whole piece.',
        'moves': [
            ('d2d4', 'd4', ''),
            ('d7d5', 'd5', ''),
            ('c2c4', 'c4', "Queen's Gambit."),
            ('e7e6', 'e6', ''),
            ('b1c3', 'Nc3', ''),
            ('g8f6', 'Nf6', ''),
            ('c1g5', 'Bg5', 'Pins the knight.'),
            ('b8d7', 'Nbd7', 'Setting the trap: the queen on d8 looks unprotected.'),
            ('c4d5', 'cxd5', ''),
            ('e6d5', 'exd5', ''),
            ('c3d5', 'Nxd5??', 'White thinks the pinned knight cannot recapture...'),
            ('f6d5', 'Nxd5!', '...but it can! It gives up the queen.'),
            ('g5d8', 'Bxd8', 'White takes the queen.'),
            ('f8b4', 'Bb4+', 'Check — the counter-punch.'),
            ('d1d2', 'Qd2', 'The only way to block.'),
            ('b4d2', 'Bxd2+', ''),
            ('e1d2', 'Kxd2', ''),
            ('e8d8', 'Kxd8', 'Material count: Black is a whole knight up.'),
        ],
    },
]

# ---------------------------------------------------------------------------
# Puzzles — "find the best move". Positions use the piece-placement part of FEN.
# ---------------------------------------------------------------------------
PUZZLES = [
    {
        'name': 'Back-rank mate',
        'theme': 'Checkmate in 1',
        'fen': '6k1/5ppp/8/8/8/8/5PPP/3R2K1',
        'to_move': 'white',
        'solution': 'd1d8',
        'san': 'Rd8#',
        'hint': "Black's own pawns trap the king on the back rank.",
        'explanation': 'The rook gives check on the 8th rank and the pawns block every escape square.',
        'goal': 'mate',
    },
    {
        'name': 'Smothered mate',
        'theme': 'Checkmate in 1',
        'fen': '6rk/6pp/8/6N1/8/8/8/6K1',
        'to_move': 'white',
        'solution': 'g5f7',
        'san': 'Nf7#',
        'hint': 'Only one piece can jump over a wall.',
        'explanation': "The king is surrounded by its own pieces. A knight check can't be blocked.",
        'goal': 'mate',
    },
    {
        'name': "Scholar's finish",
        'theme': 'Checkmate in 1',
        'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR',
        'to_move': 'white',
        'solution': 'h5f7',
        'san': 'Qxf7#',
        'hint': 'Which black square is defended only by the king?',
        'explanation': 'Queen takes f7, protected by the bishop on c4. The king cannot recapture.',
        'goal': 'mate',
    },
    {
        'name': 'Royal fork',
        'theme': 'Fork — attack two pieces at once',
        'fen': 'r3k3/8/8/3N4/8/8/8/6K1',
        'to_move': 'white',
        'solution': 'd5c7',
        'san': 'Nc7+',
        'hint': 'Find a knight check that also hits the rook.',
        'explanation': 'The knight checks the king and attacks the rook. After the king moves, Nxa8.',
        'goal': 'check',
    },
    {
        'name': 'Skewer',
        'theme': 'Skewer — attack through a piece',
        'fen': 'R7/8/4k3/8/8/8/7K/4q3',
        'to_move': 'white',
        'solution': 'a8e8',
        'san': 'Re8+',
        'hint': 'The king and queen stand on the same file.',
        'explanation': 'The rook checks the king; when it steps aside, the rook takes the queen on e1.',
        'goal': 'check',
    },
]

# ---------------------------------------------------------------------------
# Tips
# ---------------------------------------------------------------------------
TIPS = [
    ('Control the center', 'Pawns and pieces on e4, d4, e5, d5 control the most squares.'),
    ('Develop your pieces', 'Bring knights and bishops out before moving the same piece twice.'),
    ('Castle early', 'Get your king to safety and connect your rooks.'),
    ("Don't bring the queen out too early", 'It becomes a target and you lose time running away.'),
    ('Watch f7 and f2', 'In the opening these squares are defended only by the king — see the traps!'),
    ('Check, capture, threat', 'Before every move, look at all checks, captures and threats — for both sides.'),
    ('Count attackers and defenders', 'Only capture when you have more attackers than they have defenders.'),
    ('Knights on the rim are dim', 'A knight in the center controls up to 8 squares; on the edge only 4 or fewer.'),
    ('Rooks love open files', 'Put rooks on files with no pawns, and double them up.'),
    ('In the endgame, activate your king', 'With fewer pieces on the board, the king becomes a strong fighter.'),
]
