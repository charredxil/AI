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
        def swapped(li, pi, pj):
            l = li[:]
            l[pi], l[pj] = l[pj], l[pi]
            return l
        for i in look[tup[1]]:
            newpzl = swapped(tup[0], i, tup[1])
            yield (newpzl, i)
def bfs(pzl, goalpzl=['1', '2', '3', '4', '5', '6', '7', '8', ' ']):
    vis = {''.join(pzl),}
    q = deque()
    q.append([(pzl, pzl.index(' '))])
    while q:
        past = q.popleft()
        if past[-1][0] == goalpzl: return past
        for x in children(past[-1]):
            strng = ''.join(x[0])
            if strng in vis: continue
            newpast = past[:]
            newpast.append(x)
            if x[0] == goalpzl: return newpast
            q.append(newpast)
            vis.add(strng)
def run():
    puzzle = list(sys.argv[1].replace('_', ' '))
    past = bfs(puzzle)
    print(outString(past, cols=15) if past else "IMPOSSIBLE")
def test(num):
    start = time.time()
    solvable = 0
    steps = 0
    p = ['1', '2', '3', '4', '5', '6', '7', '8', ' ']
    for x in range(num):
        shuffle(p)
        pzl = p[:]
        past = bfs(pzl)
        if past:
            solvable += 1
            steps += len(past)-1
    elapsed = time.time()-start
    print("AVG T: {}".format(elapsed/num))
    print("AVG Steps: {}".format(steps/solvable))

cProfile.run('test(10)')        