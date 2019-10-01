import time, cProfile
from sys import argv, stdin
from math import log
from random import choice
import termios

def main():
    board_str = '.........'
    human_c = 'O'
    for s in argv[1:]:
        if s in 'XO': human_c = s
        if len(s) == 9: board_str = s
    x, o = 0, 0
    empty = frozenset()
    for i, c in enumerate(board_str):
        x <<= 1
        o <<= 1
        if c == 'X': x += 1
        elif c == 'O': o += 1
        else: empty |= {1 << (8-i)}
    mover = 'X' if board_str.count('X') == board_str.count('O') else 'O'
    play_game(x, o, empty, mover, human_c)

def play_game(x, o, empty, mover, human_c):
    p, np = (x, o) if mover == 'X' else (o, x)
    over = False
    winner = None
    print('Starting position:')
    display(x, o)
    print()
    while True:
        mymove = (human_c != mover)
        for wm in winmasks:
            if p & wm == wm: winner = True if mymove else False
            if np & wm == wm: winner = False if mymove else True
        if (p | np) == (1 << 9) - 1: break
        if winner is not None: break
        if mymove:
            g, b, t = tuple(map(list, partition(p, np, empty)))
            if g: move = choice(g)
            elif t: move = choice(t)
            else: move = choice(b)
            print("I played an {} at position {}.".format(mover, int(8-log(move, 2))))
        else:
            while True:
                print("Enter a position to place an {} at:".format(mover), end=' ', flush=True)
                inp = getche()
                print()
                if not str.isdigit(inp) or inp == '9':
                    print("Character '{}' is not a valid digit. Try again".format(inp))
                    continue
                move = 1 << (8-int(inp))
                if move in empty: break
                else: print("Position {} is filled. Try again.".format(inp))
        p |= move
        empty -= {move}
        display(*((p, np) if mover == 'X' else (np, p)))
        print()
        mover = 'X' if mover == 'O' else 'O'
        p, np = np, p
    print("It's a tie!" if winner is None else ("I won!" if winner else "You won!"))

already = {}
def partition(player, other, empty, allmoves=False):
    global already
    if (player, other) in already: return already[(player, other)]
    for wm in winmasks:
        if player & wm == wm: return {-1}, set(), set()
        if other & wm == wm: return set(), {-1}, set()
    if not empty: return set(), set(), {-1}
    good, bad, tie = set(), set(), set()
    for i in empty:
        _good, _bad, _tie = partition(other, player | i, empty - {i})
        if _good: bad.add(i)
        elif _tie: tie.add(i)
        else:
            good.add(i)
            if not allmoves: break
    already.update({(sym(player), sym(other)) : tuple(map(lambda k: tuple(map(sym, k)), (good, bad, tie))) for sym in symmetries})
    return good, bad, tie

def getch():
    old = termios.tcgetattr(stdin)
    new = termios.tcgetattr(stdin)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(stdin, termios.TCSANOW, new)
    key = None
    try:
        key = stdin.read(1)
    finally:
        termios.tcsetattr(stdin, termios.TCSAFLUSH, old)
    return key
getche = lambda: (lambda t: t[0])((lambda k: (k, print(k, end='', flush=True)))(getch()))

def display(x, o): print((lambda s: '\n'.join(s[i:i+3] for i in range(0, 9, 3)))(''.join(['X' if x & (1 << i) else 'O' if o & (1 << i) else '.' for i in range(8, -1, -1)])))

winmasks = [7, 7 << 3, 7 << 6, (1+8+64), (1+8+64) << 1, (1+8+64) << 2, 1+16+256, 4+16+64]
flipvert = lambda b: ((b & 73) << 2) | (b & 73*2) | ((b & 73*4) >> 2)
fliphoriz = lambda b: ((b & 7) << 6) | (b & 7*8) | ((b & 7*64) >> 6)
flipdiag1 = lambda b: (b & (4+16+64)) | ((b & 1) << 8) | ((b & (2+8)) << 4) | ((b & (128+32)) >> 4) | ((b & 256) >> 8)
flipdiag2 = lambda b: (b & (1+16+256)) | ((b & 4) << 4) | ((b & 64) >> 4) | ((b & (2+32)) << 2) | ((b & (8+128)) >> 2)
rot90 = lambda b: fliphoriz(flipdiag1(b))
rot180 = lambda b: fliphoriz(flipvert(b))
rot270 = lambda b: fliphoriz(flipdiag2(b))
identity = lambda b: b
symmetries = [flipvert , fliphoriz, flipdiag1, flipdiag2, rot90, rot180, rot270, identity]

if __name__ == "__main__": main()
