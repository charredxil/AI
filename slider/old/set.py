import sys
from collections import deque
import math
import cProfile

def outString(pzls, cols=1, steps=True):
    pzls = list(pzls)
    out = "\n"
    rows = [pzls[x:x+cols] for x in range(0, len(pzls), cols)]
    for row in rows:
        for x in range(3):
            out += "  ".join([pzl[x*3:(x+1)*3] for pzl in row]) + '\n'
        out += '\n'
    return out[:-1] + ("\nNumber of steps: {}".format(len(pzls)-1) if steps else "")
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
def bfs(pzl, finished='12345678 ', explore=False):
    q = deque([[pzl]])
    vis = set([pzl])
    dct = {}
    while q:
        past = q.popleft()
        if explore:
            if len(past)-1 in dct: dct[len(past)-1].append(past[-1])
            else: dct[len(past)-1] = [past[-1]]
        if past[-1] == finished: return past
        for x in filter(lambda x: x not in vis, nextStates(past[-1])):
            if x == finished: return past + [finished]
            q.append(past + [x])
            vis.add(x)
    if explore: return dct
def available(pzl, s, dct):
    for p in s:
        if pzl in dct[p]:
            return False
    return True
exp = bfs('12345678 ', finished='X', explore=True)
s = set()
dct = {}
for x in range(32):
    av = list(filter(lambda t: available(t, s, dct), exp[x]))
    if len(av) == 0: continue
    mn = min(av)
    s.add(mn)
    if x == 31 or x == 30:
        print(x, mn)
    dct[mn] = nextStates(mn)
print(outString(list(s), cols=10, steps=False))
print("Size of set: {}".format(len(s)))

