import sys
from collections import deque
from random import shuffle
import cProfile
import time

def outString(pzls, cols=1):
    out = "\n"
    rows = [pzls[x:x+cols] for x in range(0, len(pzls), cols)]
    for row in rows:
        for x in range(3):
            out += "  ".join([pzl[x*3:(x+1)*3] for pzl in row]) + '\n'
        out += '\n'
    return out + "Number of steps: {}".format(len(pzls)-1)
def nextStates(pzl):
    ns = []
    _ix = pzl.index(" ")
    def addNewState(delta):
        ns.append(list(pzl[:]))
        ns[-1][_ix], ns[-1][_ix+delta] = ns[-1][_ix+delta], ns[-1][_ix]
    if _ix + 3 < 9: addNewState(3)
    if _ix - 3 >= 0: addNewState(-3)
    if _ix % 3 != 2: addNewState(1)
    if _ix % 3 != 0: addNewState(-1)
    return [''.join(p) for p in ns]
def bfs(pzl):
    finished = '12345678 '
    q = deque([[pzl]])
    vis = set([pzl])
    while q:
        past = q.popleft()
        if past[-1] == finished: return past
        for x in filter(lambda x: x not in vis, nextStates(past[-1])):
            if x == finished: return past + [finished]
            q.append(past + [x])
            vis.add(x)
def run():
    puzzle = sys.argv[1].replace('_', ' ')
    past = bfs(puzzle)
    print(outString(past, cols=15) if past else "IMPOSSIBLE")
def test(num):
    start = time.time()
    solvable = 0
    steps = 0
    p = ['1', '2', '3', '4', '5', '6', '7', '8', ' ']
    for x in range(num):
        shuffle(p)
        pzl = ''.join(p)
        past = bfs(pzl)
        if past:
            solvable += 1
            steps += len(past)-1
    elapsed = time.time()-start
    print("AVG T: {}".format(elapsed/num))
    if solvable > 0: print("AVG Steps: {}".format(steps/solvable))

test(1)
