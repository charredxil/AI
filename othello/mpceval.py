from scipy import stats
from othello import *
from collections import namedtuple
import time

Line = namedtuple('Line', 'a b stderr')

def rand_board(discs, notover=True):
    while True:
        b = board_initial()
        xmove = True
        lastpass = False
        while b.discs != discs:
            moves = get_moves(b)
            move = choice([*bits(moves)]) if moves else PASS
            b = board_next(b, move)
            xmove = not xmove
            if lastpass and move == -1: break
            lastpass = move == -1
        if b.discs == discs and ((not notover) or get_moves(b) or get_moves(board_pass(b))):
            return b

ht_chk = {3:1, 4:2, 5:1, 6:2, 7:3, 8:4}
def collect_past():
    d_ht_ln = [{} for _ in range(64)]
    cur_d = None
    with open("mpcdata.txt") as f:
        ls = f.readlines()
        for l in ls:
            toks = l.split()
            if len(toks) == 1:
                cur_d = int(toks[0])
            elif len(toks) == 5:
                ht, _, a, b, stderr = tuple(toks)
                d_ht_ln[cur_d][int(ht)] = Line(float(a), float(b), float(stderr))
    return d_ht_ln


maxdepth = max(ht_chk.keys())
d_ht_ln = collect_past()
dstart = 64-maxdepth-1
while d_ht_ln[dstart]:
    dstart -= 1
limit = 60*15
for discs in range(dstart, 5, -1):
    print("Searching for {} discs...".format(discs))
    vals = [[] for x in range(maxdepth+1)]
    numboards = 0
    start = time.time()
    while time.time() - start < limit:
        numboards += 1
        b = rand_board(discs)
        searches = search(b, depthlim=maxdepth, retval=True)
        for x in range(1, maxdepth+1):
            vals[x].append(next(searches)[0])
    for ht, chk in ht_chk.items():
        s = stats.linregress(vals[chk], vals[ht])
        l = Line(s.slope, s.intercept, s.stderr)
        d_ht_ln[discs][ht] = l
    print("{} boards searched".format(numboards))
    with open("mpcdata.txt", "w") as f:
        for d, ht_ln in enumerate(d_ht_ln):
            if not ht_ln: continue
            print(d, file=f)
            for ht, ln in ht_ln.items():
                toprint = [*map(str, [ht, ht_chk[ht], ln.a, ln.b, ln.stderr])]
                print(' '.join(toprint), file=f)
