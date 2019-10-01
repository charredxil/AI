from random import choice, uniform
from math import log, inf
import sys, time, termios
import cProfile


# masks
full =    0xFFFFFFFFFFFFFFFF
corners = 0x8100000000000081
xsq     = 0x0042000000004200
top =     0x00000000000000FF
left =    0x0101010101010101
right =   0x8080808080808080
bottom =  0xFF00000000000000
noedge = full ^ (left | right)
topr = top | right
topl = top | left
botr = bottom | right
botl = bottom | left

#globals
start = None
ttable = {}
tt_on = False
h_base = None
h_black = h_white = None
h_current = None
h_order = None
hastimeout = False

# moving, bit manipulation
def allmoves(b, w, mover):
    global full, noedge
    p, o = (w, b) if mover else (b, w)
    omask = o & noedge
    moves = somemoves(p, omask, 1)
    moves |= somemoves(p, o, 8)
    moves |= somemoves(p, omask, 7)
    moves |= somemoves(p, omask, 9)
    return moves & (full ^ (p|o))
def somemoves(p, omask, delta):
    flip = ((p << delta) | (p >> delta)) & omask
    for x in range(5):
        flip |= ((flip << delta) | (flip >> delta)) & omask
    return (flip << delta) | (flip >> delta)
def moveflips(b, w, mover, mv):
    global full, noedge
    p, o = (w, b) if mover else (b, w)
    omask = o & noedge
    flip = someflips(p, omask, mv, 1)
    flip |= someflips(p, o, mv, 8)
    flip |= someflips(p, omask, mv, 7)
    flip |= someflips(p, omask, mv, 9)
    return flip & full
def someflips(p, omask, m, delta):
    flip_p = ((p << delta) | (p >> delta)) & omask
    flip_m = ((m << delta) | (m >> delta)) & omask
    for x in range(5):
        flip_p |= ((flip_p << delta) | (flip_p >> delta)) & omask
        flip_m |= ((flip_m << delta) | (flip_m >> delta)) & omask
    return flip_p & flip_m
def move(b, w, mover, mv, f=None):
    if mv == -1: return b, w, not mover
    if not f: f = moveflips(b, w, mover, mv)
    b_new = b ^ f if mover else (b | f | mv)
    w_new = (w  | f | mv) if mover else w ^ f
    return b_new, w_new, not mover
def bitcount(b):
    return bin(b).count('1')
def initial():
    b = (1 << 35) + (1 << 28)
    w = (1 << 27) + (1 << 36)
    return b, w
def bits(n):
    while n:
        b = n & (~n+1)
        yield b
        n ^= b

# I/O
fromint = lambda c: 1 << c
toint = lambda b: int(log(b, 2)) if b != -1 else -1
tocoord = lambda b: (lambda d, m: 'ABCDEFGH'[m]+str(d+1))(*divmod(toint(b), 8))
fromcoord = lambda c: fromint('ABCDEFGHabcdefgh'.index(c[0])%8 + 8*int(c[1])-8)
class Writer:
    def __init__(self, *chars):
        ['\u2500', '\u2502', '\u250c', '\u2510', '\u2514', '\u2518']
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
    def write(self, *boards, move=None, bold=0xFFFFFFFFFFFFFFFF):
        x = ['\u2500', '\u2502', '\u250c', '\u2510', '\u2514', '\u2518']
        term = __import__("termcolor") if self.color and self.grid else None
        grid, string, mv = '', '', ''
        if move and move[1] != -1: mv = self.chars[move[0]] + ' --> ' + tocoord(move[1])
        elif move and move[1] == -1: mv = '<PASS ' + self.chars[move[0]] + '>'
        count = [0 for _ in range(self.bound)]
        for ix in range(64):
            chars = [(i, t[1]) for i, t in enumerate(zip(boards, self.chars)) if (t[0] >> ix) & 1]
            for i, c in filter(lambda k: k[0] < self.bound, chars): count[i] += 1
            if ix % 8 == 0 and self.grid: grid += x[1]
            if chars:
                i, ch = chars[0]
                clr = self.colors[i] if i < len(self.colors) else 'white'
                clrd_ch = term.colored(ch, clr, attrs=(['bold'] if bold >> ix & 1 else [])) if term else '$'
                if self.grid: grid += (clrd_ch if self.color else ch) + ' '
                if self.string: string += ch if i < self.bound else '.'
            else:
                if self.grid: grid += '· '
                if self.string: string += '.'
            if ix % 8 == 7 and self.grid: grid = grid[:-1] + (' '+str(ix//8+1) if self.coords else '') +x[1]+'\n'
        if self.grid and self.coords:
            grid = x[2]+x[0]*17+x[3]+'\n{}'.format(grid)+x[1]+'A B C D E F G H  '+x[1]+'\n'+x[4]+x[0]*17+x[5]
        elif self.grid: grid = x[2]+x[0]*15+x[3]+'\n{}'.format(grid)+x[4]+x[0]*15+x[5]
        count = tuple([(self.chars[i], count[i]) for i in range(self.bound)])
        score = "SCORE: "+str(count).replace('\'', '') if self.score else ''
        if move and move[1] == -1 and self.override_on_pass: self.writestr(mv)
        else: self.writestr('\n'.join(filter(''.__ne__, [mv, grid, string, score])))
    def flush(self):
        for s in self.backlog: print(s, end=self.end)
        self.backlog = []
def board(s, bchars = 'Xx', wchars = 'Oo'):
    b = sum(1 << e if c in bchars else 0 for e, c in enumerate(s))
    w = sum(1 << e if c in wchars else 0 for e, c in enumerate(s))
    return b, w
def interpret_input(moves=False, human=False):
    b, w, mover = None, None, None
    mvs, htoken = [tuple()], []
    for s in sys.argv[1:]:
        if (s in "xo" and not human) or s in "XO": mover = s in "Oo"
        if s in "XOxo" and human: htoken = [s in 'Oo']
        if len(s) == 64: b, w = board(s)
        if s.isdigit() and moves: mvs[0] += (fromint(int(s)),)
        elif len(s) == 2 and s[1].isdigit() and s[0].isalpha() and moves:
            mvs[0] += (fromcoord(s),)
    if b is None: b, w = initial()
    if mover is None: mover = bitcount(b|w) & 1
    if htoken == [] and human: htoken = [not mover]
    return tuple([b, w, mover] + htoken + (mvs if moves else []))
def getch():
    old = termios.tcgetattr(sys.stdin)
    new = termios.tcgetattr(sys.stdin)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(sys.stdin, termios.TCSANOW, new)
    key = None
    try: key = sys.stdin.read(1)
    finally: termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, old)
    return key
getche = lambda: (lambda t: t[0])((lambda k: (k, print(k, end='', flush=True)))(getch()))

# Misc.
def autopass(b, w, mover, stopat=2, writer=False):
    passes = 0
    while allmoves(b, w, mover) == 0 and passes < stopat:
        passes += 1
        b, w, mover = move(b, w, mover, -1)
        if writer: writer.write(b, w, move=(not mover, -1))
    return b, w, mover

# board features
def f_frontier(b, w, mover):
    empty = full ^ (b|w)
    bfr = bitcount(neighbors(b) & empty)
    wfr = bitcount(neighbors(w) & empty)
    return (wfr-bfr)/(wfr+bfr) if (wfr+bfr) else 0
def f_parity(b, w, mover):
    global full
    empty = full ^ (b|w)
    odds_evens = 0
    tot = 0
    while empty:
        b = empty & (~empty+1)
        fill = floodfill(empty, b)
        empty ^= fill
        count = bitcount(fill)
        if count >= 7: continue
        odds_evens += 2*(count%2) - 1
        tot += 1
    return (odds_evens/tot) * (-1 if mover else 1) if tot else 0
def floodfill(p, b):
    while True:
        neighs = neighbors(b)
        new_b = (neighs & p) | b
        if not (new_b ^ b): break
        b = new_b
    return b
def neighbors(b):
    global left, right
    b_nl = b & ~left
    b_nr = b & ~right
    return (b << 8) | (b >> 8) | (b_nr << 1) | (b_nl >> 1) | (b_nl << 7) | (b_nr >> 7) | (b_nl >> 9) | (b_nr << 9)
def f_stable_shallow(b, w, mover):
    bst = bitcount(stable_pieces(b, shallow=3))
    wst = bitcount(stable_pieces(w, shallow=3))
    return (bst-wst)/(bst+wst) if (bst+wst) else 0
def f_stable(b, w, mover):
    bst = bitcount(stable_pieces(b))
    wst = bitcount(stable_pieces(w))
    return (bst-wst)/(bst+wst) if (bst+wst) else 0
def stable_pieces(p, shallow=-1):
    global top, left, right, bottom, topr, topl, botr, botl
    stable = 0
    iters = 0
    while True:
        iters += 1
        topbot_c = some_stable(p, stable, top, bottom, 8)
        leftright_c = some_stable(p, stable, left, right, 1)
        diag1_c = some_stable(p, stable, topr, botl, 7)
        diag2_c = some_stable(p, stable, topl, botr, 9)
        newstable = (topbot_c) & (leftright_c) & (diag1_c) & (diag2_c)
        if not (newstable ^ stable): break
        if iters == shallow: break
        stable |= newstable
    return stable
def some_stable(p, stable, prepos, preneg, delta):
    return (((stable >> delta) | prepos) | ((stable << delta) | preneg)) & p
def f_rand(b, w, mover):
    return uniform(-1, 1)
def f_score(b, w, mover):
    return bitcount(b)-bitcount(w)
def f_discs(b, w, mover):
    bd = bitcount(b)
    wd = bitcount(w)
    return (bd-wd)/(bd+wd) if (bd+wd) else 0
def f_noex(b, w, mover):
    bx = badxs(b)
    wx = badxs(w)
    return (wx-bx)/(bx+wx) if (bx+wx) else 0
def badxs(p):
    cnt = 0
    if (1 << 9) & p and not (1 << 0) & p and p: cnt += 1
    if (1 << 14) & p and not (1 << 7) & p and p: cnt += 1
    if (1 << 49) & p and not (1 << 56) & p and p: cnt += 1
    if (1 << 54) & p and not (1 << 63) & p and p: cnt += 1
    return cnt
def f_legals(b, w, mover):
    plegals = bitcount(allmoves(b, w, mover))
    olegals = bitcount(allmoves(b, w, not mover))
    diff = (plegals-olegals)/(plegals+olegals) if (plegals+olegals) else 0
    return -diff if mover else diff
def f_corners(b, w, mover):
    global corners
    bc = bitcount(b&corners)
    wc = bitcount(w&corners)
    return (bc-wc)/(bc+wc) if (bc+wc) else 0
def build(*args):
    def heur(*data):
        tot = 0
        denom = 0
        for h, wgt in args:
            denom += wgt
            tot += wgt * h(*data)
        return tot/denom
    return heur
def stage(*args):
    def heur(b, w, mover):
        discs = bitcount(b|w)
        for h, mx in args[:-1]:
            if discs <= mx:
                return h(b, w, mover)
        return args[-1][0](b, w, mover)
    return heur

### Strategy Class ###
class Strategy():
    def best_strategy(self, board, player, best_move, running):
        b, w = board(''.join(board).replace('?', ''), bchars='@', wchars='o')
        mover = player == 'o'
        for mv in search(b, w, mover, forever=True, printdata=False):
            best_move.value = toint(mv)

### OTHELLO LABS ###
def lab1(**kwargs):
    p = Writer('X', 'O', '+')
    p.grid, p.score, p.end = True, False, '\n'
    data = interpret_input()
    if not [*filter(lambda s: len(s) == 64, sys.argv[1:])]:
        p.write(*data[:2])
    a = allmoves(*data)
    p.write(*data[:2], a)
    print([*map(toint, bits(a))])
def lab2(**kwargs):
    p = Writer('X', 'O')
    #p.grid = False
    *data, mvs = interpret_input(moves=True)
    p.write(*data[:2], bold=0)
    for mv in mvs:
        data = autopass(*data, writer=p)
        flips = moveflips(*data, mv)
        data = move(*data, mv, f=flips)
        p.write(*data[:2], bold=mv|flips)
def lab3(**kwargs): lab2(**kwargs)
def lab4(**kwargs):
    p = Writer('X', 'O', '+')
    b, w, mover, htoken = interpret_input(human=True)
    history = []
    lastpass = False
    flips, mv = 0, 0
    while True:
        a = allmoves(b, w, mover)
        showmove = (not mover, mv) if mv and (mover == htoken or mv == -1) else None
        showposs = 0 if mover ^ htoken else a
        p.write(b, w, showposs, move=showmove, bold=mv|flips|showposs)
        mv = None
        if mover == htoken and a:
            while mv is None:
                print('{} -->'.format('O' if htoken else 'X'), end=' ', flush=True)
                let, num = getche(), getche()
                print()
                if let in 'ABCDEFGHabcdefgh' and num.isdigit():
                    mv = fromcoord(str.capitalize(let) + num)
                    if mv & a: break
                    else: mv = None
                print('Invalid move. Try again.')
        else: mv = [*search(b, w, mover, **kwargs)][-1] if a else -1
        history.append(str(toint(mv)))
        flips = moveflips(b, w, mover, mv)
        b, w, mover = move(b, w, mover, mv, f=flips)
        if lastpass and mv == -1: break
        lastpass = mv == -1
    p.write(b, w, 0, move=(not mover, mv))
    print(' '.join(history))
def lab5(**kwargs):
    data = interpret_input()
    a = allmoves(*data)
    intmoves = [*map(toint, bits(a))]
    print(choice(intmoves))
def lab8(**kwargs):
    global tt_on
    data = interpret_input()
    for mv, val in search(*data, getval=True, printdata=False, **kwargs):
        print(toint(mv))
def run(key='8', **kwargs):
    for s in sys.argv[1:]:
        if s[0:2] == '--': key = s[2]
    if key == 'm':
        moderator(h_black, h_white, **kwargs)
    elif key.isdigit():
        eval('lab'+key+'(**kwargs)')


# intra-program moderator
def moderator(heur_b=h_base, heur_w=h_base, **kwargs):
    global start
    p = Writer('X', 'O')
    b, w, mover = interpret_input()
    p.write(b, w, bold=0)
    history = []
    lastpass = False
    while True:
        a = allmoves(b, w, mover)
        mv = -1
        if a:
            heur = heur_w if mover else heur_b
            if heur == f_rand: mv = choice([*bits(a)])
            else:
                mv, val = [*search(b, w, mover, getval=True, heur=heur, **kwargs)][-1]
                print("Board Value:", "{:+.4g}".format(val))
        history.append(str(toint(mv)))
        flips = moveflips(b, w, mover, mv)
        b, w, mover = move(b, w, mover, mv, f=flips)
        p.write(b, w, move=(not mover, mv), bold=mv|flips)
        if lastpass and mv == -1: break
        lastpass = mv == -1
    print(' '.join(history))

# searching
totdepth = 0
numsearch = 0
def search(b, w, mover, passes=0, getval=False, timelim=2, depthlim=None, heur=None, printdata=True, forever=False):
    global start, ttable, h_current, totdepth, numsearch
    start = time.time()
    movesleft = 64 - bitcount(b|w)
    depth = 0
    ttable = {}
    h_current = heur if heur else h_base
    while forever or ((time.time() - start < timelim) if not depthlim else (depth < depthlim)):
        depth += 1
        bval = bmov = None
        if not hastimeout or depthlim is not None:
            bval, bmov = negascout(b, w, mover, depth, getmove=True)
        else:
            left = (timelim + start) - time.time()
            try:
                with timeout(seconds=left):
                    bval, bmov = negascout(b, w, mover, depth, getmove=True)
            except TimeoutError:
                continue
        yield (bmov, bval) if getval else bmov
        if depth > movesleft: break
    totdepth += depth
    numsearch += 1
    if printdata:
        print("Plies:", depth)
        print('Avg Plies: {:.4g}'.format(totdepth/numsearch))

def negascout(b, w, mover, depth, passes=0, getmove=False):
    neg = _negascout(b, w, mover, depth, -inf, inf, passes, getmove=getmove)
    if getmove and mover: neg = -neg[0], neg[1]
    elif mover: neg *= -1
    return neg
def _negascout(b, w, mover, depth, alpha, beta, passes=0, getmove=False):
    # retrieve from transposion table
    global ttable, tt_on
    if tt_on:
        ttentry = ttable.get((b, w, mover))
        if ttentry and ttentry[2] >= depth:
            tt_val, tt_move, tt_depth, tt_flag = ttentry
            if tt_flag == 0:
                return (tt_val, tt_move) if getmove else tt_val
            elif tt_flag == -1: alpha = max(alpha, tt_val)
            elif tt_flag == 1: beta = min(beta, tt_val)
            if alpha >= beta:
                return (tt_val, tt_move) if getmove else tt_val

    # check if state is a leaf node
    if depth == 0 or passes == 2:
        h = f_score(b, w, mover) if passes == 2 else h_current(b, w, mover)
        trueh = -h if mover else h
        return (trueh, 0) if getmove else trueh

    al = alpha
    be = beta
    best = -inf, 0
    moves = allmoves(b, w, mover)
    # if a pass is necessary
    if not moves:
        best = -_negascout(b, w, not mover, depth, -beta, -alpha, passes+1), -1
    # search all moves
    else:
        ordered_moves = allmoves_ordered(b, w, mover, depth, moves=moves)
        for ix, (mv, newdata) in enumerate(ordered_moves):
            v = -_negascout(*newdata, depth-1, -be, -al)
            if al < v < beta and ix > 0:
                v = -_negascout(*newdata, depth-1, -beta, -alpha)
            if v > best[0]: best = (v, mv)
            al = max(al, v)
            if al >= beta: break
            be = al + 1

    # enter into transposion table
    if tt_on:
        tt_flag = None
        if best[0] <= alpha: tt_flag = 1
        elif best[0] >= beta: tt_flag = -1
        else: tt_flag = 0
        ttable[(b, w, mover)] = (*best, depth, tt_flag)

    return best if getmove else best[0]

def allmoves_ordered(b, w, mover, depth, moves=None):
    global tt_on, ttable, h_order
    if not moves: moves = allmoves(b, w, mover)
    tt_move = None
    if tt_on:
        ttentry = ttable.get((b, w, mover))
        if ttentry: tt_move = ttentry[1], move(b, w, mover, ttentry[1])
    val_mvdata = []
    for mv in bits(moves):
        if tt_move and mv == tt_move[0]: continue
        newdata = move(b, w, mover, mv)
        h = h_order(*newdata) * (1 if mover else -1)
        val_mvdata.append((h, mv, newdata))
    ordered = [t[1:] for t in sorted(val_mvdata)]
    if tt_move: return [tt_move, *ordered]
    return ordered


# full heuristics
h_deep = build((f_discs, 0.05), (f_frontier, 3), (f_legals, 1), (f_noex, 100), (f_stable, 300), (f_corners, 300))
h_early = build((f_discs, -0.1), (f_legals, 5), (f_noex, 100), (f_corners, 400))
h_late = build((f_discs, 0.05), (f_stable, 300), (f_parity, 300))
h_promise = build((f_legals, 1), (f_frontier, 3), (f_noex, 100), (f_stable_shallow, 200))
# staged heuristics
hs_tres = stage((h_early, 12), (h_deep, 45), (h_late, 64))

#setting globals
h_base = hs_tres
h_order = h_promise
tt_on = True
hastimeout = False
if hastimeout: from timeout import timeout
if __name__ == "__main__":
    h_black = h_white = f_rand
    run('m', forever=True)
    #cProfile.run("run('m', depthlim=7)")
