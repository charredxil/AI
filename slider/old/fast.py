import sys
from collections import deque
from random import shuffle
import cProfile
import time

look = [{1, 3}, {0, 2, 4}, {1, 5}, {0, 4, 6}, {1, 3, 5, 7}, {2, 4, 8}, {3, 7}, {4, 6, 8}, {7, 5}]
def outString(nodes, cols=1):
    out = "\n"
    pzls = [node.pzl for node in nodes]
    rows = [pzls[x:x+cols] for x in range(0, len(pzls), cols)]
    for row in rows:
        for x in range(3):
            out += "  ".join([pzl[x*3:(x+1)*3] for pzl in row]) + '\n'
        out += '\n'
    return out + "Number of steps: {}".format(len(pzls)-1)
def children(tup):
        def swapstr(s, i, j):
            if i < j: return s[:i] + s[j] + s[i+1:j] + s[i] + s[j+1:]
            else: return s[:j] + s[i] + s[j+1:i] + s[j] + s[i+1:]
        for i in look[tup[1]]:
            newpzl = swapstr(tup[0], i, tup[1])
            yield (newpzl, i)
def bfs(pzl, goalpzl='12345678 '):
    vis = {pzl,}
    q = deque()
    q.append([(pzl, pzl.index(' '))])
    while q:
        past = q.popleft()
        if past[-1][0] == goalpzl: return past
        for x in children(past[-1]):
            if x[0] in vis: continue
            newpast = past[:]
            newpast.append(x)
            if x[0] == goalpzl: return newpast
            q.append(newpast)
            vis.add(x[0])
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
    print("AVG Steps: {}".format(steps/solvable))

cProfile.run('test(10)')        