import sys, time, cProfile
from math import log

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
already = {}
def partition(player, other, empty, allmoves=False):
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
    already.update({(sym(player), sym(other)) : (good, bad, tie) for sym in symmetries})
    return good, bad, tie
#def select_move(p, o):
def main():
    b_str = sys.argv[1]
    x, o = 0, 0
    empty = frozenset()
    for i, c in enumerate(b_str):
        x <<= 1
        o <<= 1
        if c == 'X': x += 1
        elif c == 'O': o += 1
        else: empty |= {1 << (8-i)}
    p, np = (x, o) if b_str.count('X') == b_str.count('O') else (o, x)
    display(x, o)
    print('Mover:', '"X"' if b_str.count('X') == b_str.count('O') else '"O"' ,sep='\t\t')
    start = time.time()
    moves = tuple(map(lambda f: {int(log(m, 2)) for m in f} if f else None, partition(p, np, empty, allmoves=True)))
    print("Good moves:\t{}\nBad moves:\t{}\nTying moves:\t{}".format(*moves))
    print("Elapsed time:\t{} secs".format(time.time()-start))

if __name__ == "__main__": main()
