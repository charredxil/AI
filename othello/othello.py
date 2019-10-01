from random import choice
from math import log, inf
from collections import namedtuple
import cProfile, time, sys
import functools
import flips

# Globals & Constants
feats = None
profile = False
hastimeout = True
if hastimeout: from timeout import timeout
ttable = None
probcutting = None

Board = namedtuple('Board', 'p o discs')
Entry = namedtuple('Entry', 'value flag depth move')
Param = namedtuple('Param', 'check cut a b s')

full = 0xFFFFFFFFFFFFFFFF
noedge = 0x7e7e7e7e7e7e7e7e
corners = 0x8100000000000081
xsq = 0x0042000000004200
csq = 0x4281000000008142
bsq = 0x2400810000810024
asq = 0x1800008181000018
top = 0x00000000000000FF
left = 0x0101010101010101
right = 0x8080808080808080
bottom = 0xFF00000000000000
topbot = top | bottom
leftright = left | right
edges = topbot | leftright
LOWER, EXACT, UPPER = -1, 0, 1
RANDOM = 666
PASS = -1

#I/O
def moderate(x_heur, o_heur, **kwargs):
    global h_current, probcutting
    w = Writer('X', 'O')
    b, xmove = interpret_input()
    w.write(b, xmove)
    history = []
    lastpass = False
    while True:
        moves = get_moves(b)
        move = PASS
        if moves:
            h_current = x_heur if xmove else o_heur
            if h_current == RANDOM: move = choice([*bits(moves)])
            else:
                val, move = [*search(b, retval=True, printdata=True, **kwargs)][-1]
                trueval = val*(1 if xmove else -1)
                pval = "{:+.2g}".format(trueval if abs(trueval) <= 64 else trueval//100)
                print("Board Value:", pval + ('M' if abs(trueval) > 64 else ''))
        history.append(str(toint(move)))
        flips = get_flips(b, move)
        b = board_next(b, move, flips=flips)
        xmove = not xmove
        w.write(b, xmove, move=(xmove, move), bold=move|flips)
        if lastpass and move == PASS: break
        lastpass = move == PASS
    print(' '.join(history))
    return b, xmove
def interpret_input():
    boardstr = xmove = None
    for s in sys.argv[1:]:
        if len(s) == 64: boardstr = s
        elif len(s) == 1: xmove = s in 'Xx'
    if boardstr is None: boardstr = '...........................OX......XO...........................'
    if xmove is None: xmove = boardstr.count('.') % 2 == 0
    return string_to_board(boardstr, xmove), xmove
def string_to_board(s, xmove, bchars = 'Xx', wchars = 'Oo'):
    b = sum(1 << e if c in bchars else 0 for e, c in enumerate(s))
    w = sum(1 << e if c in wchars else 0 for e, c in enumerate(s))
    p, o = (b, w) if xmove else (w, b)
    return Board(p, o, 64-s.count('.'))
fromint = lambda c: 1 << c
toint = lambda b: int(log(b, 2)) if b != PASS else PASS
tocoord = lambda b: (lambda d, m: 'ABCDEFGH'[m]+str(d+1))(*divmod(toint(b), 8))
fromcoord = lambda c: fromint('ABCDEFGHabcdefgh'.index(c[0])%8 + 8*int(c[1])-8)

class Writer:
    def __init__(self, *chars):
        self.end = '\n\n'
        self.grid = True
        self.coords = True
        self.override_on_pass = True
        self.string = True
        self.score = True
        self.bound = min(2, len(chars))
        self.autoflush = True
        self.color = True
        self.backlog = []
        self.chars = chars
        self.colors = ('magenta', 'yellow', 'green', 'red')
    def writestr(self, s):
        if self.autoflush: print(s, end=self.end)
        else: self.backlog.append(s)
    def write(self, b, xmove, *aux, move=None, bold=0):
        u = ['\u2500', '\u2502', '\u250c', '\u2510', '\u2514', '\u2518']
        x_o = (b.p, b.o) if xmove else (b.o, b.p)
        boards = [*x_o, *aux]
        term = __import__("termcolor") if self.color and self.grid else None
        grid, string, mv = '', '', ''
        if move and move[1] != PASS: mv = self.chars[move[0]] + ' --> ' + tocoord(move[1])
        elif move and move[1] == PASS: mv = '<PASS ' + self.chars[move[0]] + '>'
        count = [0 for _ in range(self.bound)]
        for ix in range(64):
            chars = [(i, t[1]) for i, t in enumerate(zip(boards, self.chars)) if (t[0] >> ix) & 1]
            for i, c in filter(lambda k: k[0] < self.bound, chars): count[i] += 1
            if ix % 8 == 0 and self.grid: grid += u[1]
            if chars:
                i, ch = chars[0]
                clr = self.colors[i] if i < len(self.colors) else 'white'
                clrd_ch = term.colored(ch, clr, attrs=(['bold'] if (bold >> ix) & 1 else [])) if term else '$'
                if self.grid: grid += (clrd_ch if self.color else ch) + ' '
                if self.string: string += ch if i < self.bound else '.'
            else:
                if self.grid: grid += '· '
                if self.string: string += '.'
            if ix % 8 == 7 and self.grid: grid = grid[:-1] + (' '+str(ix//8+1) if self.coords else '') +u[1]+'\n'
        if self.grid and self.coords:
            grid = u[2]+u[0]*17+u[3]+'\n{}'.format(grid)+u[1]+'A B C D E F G H  '+u[1]+'\n'+u[4]+u[0]*17+u[5]
        elif self.grid: grid = u[2]+u[0]*15+u[3]+'\n{}'.format(grid)+u[4]+u[0]*15+u[5]
        count = tuple([(self.chars[i], count[i]) for i in range(self.bound)])
        score = "SCORE: "+str(count).replace('\'', '') if self.score else ''
        if move and move[1] == PASS and self.override_on_pass: self.writestr(mv)
        else: self.writestr('\n'.join(filter(''.__ne__, [mv, grid, string, score])))
    def flush(self):
        for s in self.backlog: print(s, end=self.end)
        self.backlog = []

# Board manipulation
def board_pass(b):
    return Board(b.o, b.p, b.discs)
def board_next(b, x, flips=None):
    if x == PASS: return board_pass(b)
    flips = get_flips(b, x) if flips is None else flips
    p = b.p ^ (flips | x)
    o = b.o ^ flips
    return Board(o, p, b.discs+1)
def board_initial():
    p = (1 << 35) + (1 << 28)
    o = (1 << 27) + (1 << 36)
    return Board(p, o, 4)

# Bit manipulation
def get_moves(b):
    mask = b.o & noedge
    return (get_moves_dir(b.p, 1, mask)| get_moves_dir(b.p, 8, b.o) | get_moves_dir(b.p, 7, mask) | get_moves_dir(b.p, 9, mask)) & (full ^ (b.p|b.o))
def get_moves_dir(p, dr, mask):
    dr2 = dr << 1
    dr4 = dr << 2
    flip_l  = p | (mask & (p << dr));    flip_r  = p | (mask & (p >> dr))
    mask_l  = mask & (mask << dr);       mask_r  = mask & (mask >> dr)
    flip_l |= mask_l & (flip_l << dr2);  flip_r |= mask_r & (flip_r >> dr2)
    mask_l &= (mask_l << dr2);           mask_r &= (mask_r >> dr2)
    flip_l |= mask_l & (flip_l << dr4);  flip_r |= mask_r & (flip_r >> dr4)
    return ((flip_l & mask) << dr) | ((flip_r & mask) >> dr)
def _get_moves_dir(p, dr, mask):
    flip = ((p << dr) | (p >> dr)) & mask
    for x in range(5):
        flip |= ((flip << dr) | (flip >> dr)) & mask
    return (flip << dr) | (flip >> dr)
def get_flips(b, x):
    xpos = x.bit_length()-1
    return flips.func[xpos](b.p, b.o)
def _get_flips(b, x):
    mask = b.o & noedge
    return (get_flips_dir(b.p, x, 1, mask) | get_flips_dir(b.p, x, 8, b.o) | get_flips_dir(b.p, x, 7, mask) | get_flips_dir(b.p, x, 9, mask))
def get_flips_dir(p, x, dr, mask):
    flip_p = ((p << dr) | (p >> dr)) & mask
    flip_x = ((x << dr) | (x >> dr)) & mask
    for x in range(5):
        flip_p |= ((flip_p << dr) | (flip_p >> dr)) & mask
        flip_x |= ((flip_x << dr) | (flip_x >> dr)) & mask
    return flip_p & flip_x
def popcnt(x):
    x -= (x >> 1) & 0x5555555555555555
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    return ((x * 0x0101010101010101) & 0xffffffffffffffff ) >> 56
def popcnt_low(x):
    count = 0
    while x:
        b = x & -x
        x ^= b
        count += 1
    return count
def bits(n):
    while n:
        b = n & -n
        yield b
        n ^= b

# Searching
totdepth = 0
numsearch = 0
h_current = None
def search(b, timelim=inf, depthlim=inf, heuristic=None, retval=False, printdata=False):
    global ttable, totdepth, numsearch, hastimeout, h_current
    if heuristic is not None:
        h_current = heuristic
    start = time.time()
    ttable = {}
    depthlim = min(depthlim, 65-b.discs)
    depth = 0
    while (time.time() - start < timelim):
        depth += 1
        val = move = None
        if not hastimeout or timelim == inf:
            val, move = pvs(b, depth, -inf, inf, retmove=True)
        else:
            left = (timelim + start) - time.time()
            try:
                with timeout(seconds=left):
                    val, move = pvs(b, depth, -inf, inf, retmove=True)
            except TimeoutError:
                pass
        if move is None: break
        yield (val, move) if retval else move
        if depth >= depthlim: break
    totdepth += depth
    numsearch += 1
    if printdata:
        print("Plies:", depth)
        print('Avg Plies: {:.4g}'.format(totdepth/numsearch))

probcut_data = None
mpc_data = None
probcutting = False
def pvs(b, depth, alpha, beta, passes=0, retmove=False):
    entry = ttable.get(b)
    if entry and entry.depth >= depth:
        if entry.flag == LOWER:
            alpha = max(alpha, entry.value)
        if entry.flag == UPPER:
            beta = min(beta, entry.value)
        if entry.flag == EXACT or alpha >= beta:
            return (entry.value, entry.move) if retmove else entry.value

    if passes == 2:
        return score(b)
    if depth == 0:
        return h_current(b)

    if probcutting and not retmove:
        if mpc_data[b.discs] and depth in mpc_data[b.discs]:
            p = mpc_data[b.discs][depth]
            if beta != inf:
                bound = round((p.cut*p.s + beta - p.b)/p.a)
                if pvs(b, p.check, bound-1, bound) >= bound:
                    return beta
            if alpha != -inf:
                bound = round((-p.cut*p.s + alpha - p.b)/p.a)
                if pvs(b, p.check, bound, bound+1) <= bound:
                    return alpha

    al, be = alpha, beta
    bestmove = None
    bestval = -inf
    children = ordered_moves(b)
    for ix, (move, child) in enumerate(children):
        n_passes, n_depth = (passes+1, depth) if move == PASS else (0, depth-1)
        v = -pvs(child, n_depth, -be, -al, passes=n_passes)
        if al < v < beta and ix > 0:
            v = -pvs(child, n_depth, -beta, -alpha, passes=n_passes)
        if v > bestval:
            bestval, bestmove = v, move
        al = max(al, v)
        if al >= beta: break
        be = al + 1

    flag = None
    if al <= alpha: flag = UPPER
    elif al >= beta: flag = LOWER
    else: flag = EXACT
    ttable[b] = Entry(al, flag, depth, bestmove)

    return (bestval, bestmove) if retmove else bestval

h_order = None
def ordered_moves(b):
    moves = get_moves(b)
    if not moves: return [(PASS, board_pass(b))]
    tmove = None
    entry = ttable.get(b)
    if entry is not None:
        tmove = entry.move
    move_child = [(x, board_next(b, x)) for x in bits(moves) if x != tmove]
    move_child.sort(key=lambda t: h_order(t[1]))
    if tmove is not None:
        return [(tmove, board_next(b, tmove)), *move_child]
    return move_child

#Probcut data
def get_probcut_data(filename):
    disc_line = [None for _ in range(65)]
    with open(filename) as f:
        ls = f.readlines()
        for l in ls:
            toks = l.split()
            if len(toks) != 4: continue
            d, a, b, stderr = tuple(toks)
            disc_line[int(d)] = (float(a), float(b), float(stderr))
    return disc_line
def get_mpc_data(filename, string=None):
    d_ht_param = [{} for _ in range(65)]
    cur_d = None
    if not string:
        with open(filename) as f:
            string = f.read()
    ls = string.splitlines()
    for l in ls:
        toks = l.split()
        if len(toks) == 1:
            cur_d = int(toks[0])
        elif len(toks) == 5:
            ht, chk, a, b, s = tuple(toks)
            cut = 1.0 if cur_d < 36 else 1.4
            d_ht_param[cur_d][int(ht)] = Param(int(chk), cut, float(a), float(b), float(s))
    return d_ht_param

# Features & Heuristic Misc.
def from_txt(filename, feats, h_default):
    heur = [None for _ in range(64)] + [score]
    for line in open(filename):
        toks = line.split()
        if len(toks) != len(feats)+1: continue
        weights = tuple(map(int, toks[1:]))
        int(toks[0])
        heur[int(toks[0])] = combine(feats, weights)
    current = None
    for ix in range(len(heur)-2, -1, -1):
        if heur[ix] is None:
            heur[ix] = current if current else h_default
        else: current = heur[ix]
    return (lambda b: heur[b.discs](b))
def score(b):
    return 100*(popcnt(b.p) - popcnt(b.o))
def f_discs(b):
    pd = popcnt(b.p)
    od = popcnt(b.o)
    return normalize(pd, od)
def f_moves(b):
    pm = popcnt(get_moves(b))
    om = popcnt(get_moves(board_pass(b)))
    return normalize(pm, om)
def f_corners(b):
    pc = popcnt_low(b.p & corners)
    oc = popcnt_low(b.o & corners)
    return normalize(pc, oc)
def f_xsquares(b):
    px = badxs(b.p)
    ox = badxs(b.o)
    return normalize(px, ox)
def badxs(p):
    notc = (p & corners) ^ corners
    px = p & xsq
    notcx = (notc << 9) | (notc << 7) | (notc >> 9) | (notc >> 7)
    return popcnt_low(notcx & px)
def f_csquares(b):
    pc = badcs(b.p)
    oc = badcs(b.o)
    return normalize(pc, oc)
def badcs(p):
    notco = (p & corners) ^ corners
    notco_nl = notco & ~left
    notco_nr = notco & ~right
    notco_c = (notco_nr << 1) | (notco_nl >> 1) | (notco >> 8) | (notco << 8)
    return popcnt_low(notco_c & p)
def f_parity(b):
    return 64 if (b.discs % 2) else -64
def f_frontier(b):
    empty = full ^ (b.p|b.o)
    pfr = popcnt(neighbors(b.p) & empty)
    ofr = popcnt(neighbors(b.o) & empty)
    return normalize(pfr, ofr)
def neighbors(p):
    p_nl = p & ~left
    p_nr = p & ~right
    return (p << 8) | (p >> 8) | (p_nr << 1) | (p_nl >> 1) | (p_nl << 7) | (p_nr >> 7) | (p_nl >> 9) | (p_nr << 9)
def f_stable(b):
    ps = popcnt(stable_pieces(b.p, depth=4))
    os = popcnt(stable_pieces(b.o, depth=4))
    return normalize(ps, os)
def f_stable_nc(b):
    ps = popcnt(stable_pieces(b.p, depth=4) & (~corners))
    os = popcnt(stable_pieces(b.o, depth=4) & (~corners))
    return normalize(ps, os)
def stable_pieces(p, depth=-1):
    iters = 0
    stable = 0
    while iters != depth:
        newstable = (p & some_stable(stable, topbot, 8) & some_stable(stable, leftright, 1) & some_stable(stable, edges, 7) & some_stable(stable, edges, 9)) | stable
        if newstable == stable: break
        stable = newstable
        iters += 1
    return stable
def some_stable(stable, pre, delta):
    return (stable >> delta) | (stable << delta) | pre
def normalize(a, b):
    return 64*(a-b)/(a+b) if (a+b) else 0
def combine(funcs, weights):
    totweights = sum(abs(w) for w in weights)
    weights = [w/totweights for w in weights]
    def h(b):
        tot = 0
        for f, w in zip(funcs, weights):
            tot += w*f(b)
        return tot
    return h

feats1 = (f_discs, f_moves, f_frontier, f_stable, f_corners, f_xsquares, f_csquares, f_parity)
feats2 = (f_discs, f_moves, f_frontier, f_stable_nc, f_corners, f_xsquares, f_csquares, f_parity)
# Heuristics
h_4 = combine((f_moves, f_frontier, f_corners, f_xsquares, f_csquares, f_stable), (1, -5, 1000, -300, -30, 100))
h_txt2 = from_txt('theur.txt', feats2, h_4)

h_current = h_txt2
h_order = combine((f_frontier, f_corners, f_xsquares), (-1, 200, -60))
#probcut_data = get_probcut_data("probcutdata.txt")
mpc_data = get_mpc_data("mpcdata.txt")
probcutting = True
def main():
    b, xmove = moderate(h_txt2, h_txt2, timelim=2)
if __name__ == '__main__':
    if not '--p' in sys.argv[1:]: main()
    else: cProfile.run('main()')

class Strategy:
    def best_strategy(self, board, player, best_move, still_running):
        xmove = player == "@"
        bstr = ''.join(board).replace('?', '')
        b = string_to_board(bstr, xmove, bchars='@')
        moves = search(b)
        while True:
            mv = toint(next(moves))
            best_move.value = 11 + (mv//8)*10 + (mv%8)
