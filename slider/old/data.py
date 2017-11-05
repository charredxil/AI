import sys
from collections import deque
import math
import cProfile

def outString(pzls, cols=1):
    pzls = list(pzls)
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
def bfs(pzl, finished='12345678 ', explore=False):
    q = deque([[pzl]])
    vis = set([pzl])
    dct = {}
    while q:
        past = q.popleft()
        if explore:
            if len(past)-1 in dct: dct[len(past)-1].append(past)
            else: dct[len(past)-1] = [past]
        if past[-1] == finished: return past
        for x in filter(lambda x: x not in vis, nextStates(past[-1])):
            if x == finished: return past + [finished]
            q.append(past + [x])
            vis.add(x)
    if explore: return dct
def displayExp(exp, spacing=15):
    maxSteps = max((key for key in exp))
    half = math.ceil(maxSteps / 2)
    print("\nMaxSteps: {}\n".format(maxSteps))
    for i in range(half):
        col1 = "{}: {}".format(i, len(exp[i]))
        print(col1+' '*(spacing-len(col1)), end='')
        print(i+half, len(exp[i+half]), sep=": ")
    print(outString(reversed(exp[maxSteps][0]), cols = 15))
def run():
    exp = bfs('12345678 ', finished='X', explore=True)
    displayExp(exp)

run()
