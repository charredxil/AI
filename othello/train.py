from random import choice, uniform, sample, randint, shuffle, normalvariate
from othello import *
from math import inf
import time
from timeout import timeout
import sys
import re

filename = 'logh.txt'
gamefilename = 'xxx.gam'
feats = (f_discs, f_moves, f_frontier, f_stable_nc, f_corners, f_xsquares, f_csquares, f_parity)
per = 3

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
def boardset(k, disclo, dischi):
    lines = open(gamefilename).readlines()
    ixs = sample(range(len(lines)), k)
    bs = []
    for i in ixs:
        l = lines[i]
        b = board_initial()
        discnum = randint(disclo, dischi)
        moves = [*map(fromcoord, re.findall(r"[a-h][1-8]", l))]
        for mv in moves:
            while not get_moves(b):
                b = board_pass(b)
            b = board_next(b, mv)
            if b.discs >= discnum: break
        bs.append(b)
    shuffle(bs)
    return bs
def collect_past(filename):
    heur = [None for _ in range(64)] + [score]
    hnums = [None for _ in range(64)] + [-1]
    for line in open(filename):
        toks = line.split()
        if len(toks) < len(feats)+1: continue
        ix = int(toks[0])
        weights = tuple(map(int, toks[1:]))
        h_ix = combine(feats, weights)
        for i in range(ix-2, ix+1):
            heur[i] = h_ix
        hnums[ix] = weights
    return heur, hnums
def write_tofile(hnums, filename):
    with open(filename, 'w') as f:
        for ix, ws in enumerate(hnums):
            if ws is None or ws == -1: continue
            line = ' '.join([*map(str, [ix, *ws])])
            print(line, file=f)

def new_slot(heur):
    ix = 64
    while heur[ix] is not None: ix -= 1
    return ix
def stage(heur):
    heurc = heur.copy()
    h = None
    for ix in range(len(heur)-1, -1, -1):
        if heur[ix] is None:
            heurc[ix] = h if h is not None else h_1
        else:
            h = heur[ix]
    return (lambda b: heurc[b.discs](b))

def autosize(fullheur, discs):
    depth = 1
    bs = [rand_board(randint(discs-per, discs)) for _ in range(5)]
    possavg = 0
    while True:
        try:
            with timeout(seconds=15):
                avg = sum(timesearch(fullheur, b, depthlim=depth) for b in bs)/5
        except TimeoutError:
            numb = int(((30*60)/possavg)/2)
            numb = min(60561, numb)
            return numb, numb, depth-1
        if depth == 16:
            numb = int(((30*60)/possavg)/2)
            numb = min(60561, numb)
            return numb, numb, depth-1
        possavg = avg
        depth+=1
def timesearch(fullheur, b, **kwargs):
    start = time.time()
    l = [*search(b, heuristic=fullheur, **kwargs)]
    return time.time()-start

def getsets(heur, discs, trainsize=None, testsize=None, depth=None):
    fullheur = stage(heur)
    print("Training for {} discs...".format(discs if per == 1 else (str(discs-per+1)+'-'+str(discs))))
    if not depth:
        trainsize, testsize, depth = autosize(fullheur, discs)
    boards = boardset(trainsize+testsize, discs-per, discs)
    train = boards[:trainsize]
    test = boards[trainsize:]
    #train = [rand_board(randint(discs-per, discs)) for _ in range(trainsize)]
    #test = [rand_board(randint(discs-per, discs)) for _ in range(testsize)]
    print("Training/Test Boards Retrieved")
    print("Searcing with Depth {}, and {} Boards per Set".format(depth, trainsize))
    actual = []
    actual_t = []
    start = time.time()
    for tb in train:
        val, move = [*search(tb, heuristic=fullheur, retval=True, depthlim=depth)][-1]
        if abs(val) > 70: val = val // 100
        actual.append(val)
    for tb in test:
        val, move = [*search(tb, heuristic=fullheur, retval=True, depthlim=depth)][-1]
        if abs(val) > 70: val = val // 100
        actual_t.append(val)

    w = Writer('X', 'O')
    w.score, w.end = False, '\n'
    w.write(train[0], True)
    print("Sample Score:", actual[0])
    print()
    elaps = (time.time() - start)
    avg_t = elaps/(trainsize + testsize)
    print("Training/Test Board Values Found")
    print("Total Search Time:  {:+.3g} s".format(elaps))
    print("AVG Time per Board: {:+.3g} s".format(avg_t))

    f_train = [tuple(ft(b) for ft in feats) for b in train]
    f_test = [tuple(ft(b) for ft in feats) for b in test]
    return train, actual, f_train, test, actual_t, f_test

def train(train, actual, f_train, test, actual_t, f_test):
    weights = tuple(normalvariate(0, 1.5) for _ in feats)
    olderr = train_err = inf
    while True:
        train_err, grad, p, m = errdata(weights, f_train, train, actual)
        if olderr - train_err < 0.0001:
            break
        weights = new_weights(weights, f_train, train, actual, train_err, p, m)
        olderr = train_err

    mult = min(abs(w) for w in weights)
    weights = tuple(int((10/mult)*w+(0.5 if w > 0 else -0.5)) for w in weights)
    print("Weights:       ", weights)
    test_err = errdata(weights, f_test, test, actual_t, data=False)
    print("Training ERROR:", train_err**0.5)
    print("Test ERROR:    ", test_err**0.5)
    return test_err, weights

def train_trials(*args, n=20):
    trials = []
    for i in range(1, n+1):
        print()
        print("#"+str(i))
        trials.append(train(*args))
    err, weights = min(trials)
    print()
    print("FINAL Weights: ", weights)
    print("FINAL ERROR:   ", err**0.5)
    print()
    return weights

def errdata(weights, f, boards, actual, data=True):
    n = len(boards)
    totw = sum(abs(w) for w in weights)
    h = [sum(w*ft for w, ft in zip(weights, tup_f))/totw for tup_f in f]
    err = sum((h[x]-actual[x])**2 for x in range(n))/n
    if not data: return err
    grad = [(2/n)*sum(f[x][i]*(h[x]-actual[x]) for x in range(n)) for i in range(len(weights))]
    mag = sum(t**2 for t in grad)**0.5
    p = [-t/mag for t in grad]
    m = sum(grad[i]*p[i] for i in range(len(weights)))
    return err, grad, p, m
def new_weights(weights, f, train, actual, err, p, m, a=1000, tau=0.5, c=0.01):
    t = -c*m
    while True:
        n_weights = tuple(w + a*pi for w, pi in zip(weights, p))
        n_err = errdata(n_weights, f, train, actual, data=False)
        if err - n_err >= a*t:
            return n_weights
        a *= tau

def make_new(**kwargs):
    heur, hnums = collect_past(filename)
    ix = new_slot(heur)
    data = getsets(heur, ix, **kwargs)
    weights = train_trials(*data)
    hnums[ix] = weights
    write_tofile(hnums, filename)

if __name__ == "__main__":
    while True:
        ll = list(open(filename))
        if ll:
            fl = ll[0].split()
            if int(fl[0]) <= 7: break
        make_new()
