import sys
from collections import deque
isgoal = lambda pzl: pzl[1] == 1
c = lambda p, ix, ch: p[:ix] + ch + p[ix+1:]
def nbr(p, start, over, dest):
    n = c(c(c(p[0], start, '.'), over, '.'), dest, 'P')
    return ((n, p[1]-1), (start, dest))
def all_nbrs(p):
    for ix in range(15):
        if p[0][ix] != '.': continue
        for a, b in adj[ix]:
            if p[0][a] == '.' or p[0][b] == '.': continue
            yield nbr(p, b, a, ix)
def bfs(root):
    prev = {}
    vis = set()
    q = deque([root])
    while True:
        node = q.popleft()
        for x, jump in all_nbrs(node):
            if x in vis: continue
            prev[x] = (node, jump)
            if isgoal(x): return path(x, prev)
            q.append(x)
            vis.add(x)
def path(cur, prev):
    path = []
    while cur in prev:
        cur, j = prev[cur]
        path.append(j)
    path.reverse()
    return path

adj = {0: {(2, 5), (1, 3)}, 1: {(3, 6), (4, 8)}, 2: {(5, 9), (4, 7)}, 3: {(4, 5), (7, 12), (1, 0), (6, 10)}, 4: {(7, 11), (8, 13)}, 5: {(2, 0), (9, 14), (4, 3), (8, 12)}, 6: {(3, 1), (7, 8)}, 7: {(8, 9), (4, 2)}, 8: {(7, 6), (4, 1)}, 9: {(5, 2), (8, 7)}, 10: {(6, 3), (11, 12)}, 11: {(7, 4), (12, 13)}, 12: {(13, 14), (7, 3), (11, 10), (8, 5)}, 13: {(12, 11), (8, 4)}, 14: {(9, 5), (13, 12)}}
puzz_str = 'PPPPPPPPPPPPPPP'
i = int(sys.argv[1]) if len(sys.argv) > 1 else 4
puzz = (puzz_str[:i] + '.' + puzz_str[i+1:], 14)
jumps = bfs(puzz)
for j in jumps: print("{} --> {}".format(*j))


