def breadthFirstSearch(pzl, q, vis):
    while q and q[0][-1] != '12345678 ': (lambda past: [q.append((lambda _: past + [x])(vis.add(x))) for x in filter(lambda x: x not in vis, (lambda pzl: [''.join(p) for p in [(lambda delta, ix: (lambda lst, i, j, elemi, elemj: (lst.pop(i), (lst.insert(i, elemj), (lst.pop(j), (lst.insert(j, elemi), lst)[1])[1])[1])[1])(list(pzl[:]), ix, ix+delta, pzl[ix], pzl[ix+delta]))(delta, pzl.index(' ')) for delta, cond in [(3, lambda x: x + 3 < 9), (-3, lambda x: x - 3 >= 0), (1, lambda x: x % 3 != 2), (-1, lambda x: x % 3 != 0)] if cond(pzl.index(" "))]])(past[-1]))])(q.popleft())
    return q[0]
print((lambda pzls, cols: '\n\n'.join('\n'.join(["  ".join([pzl[x*3:(x+1)*3] for pzl in row]) for x in range(3)]) for row in [pzls[x:x+cols] for x in range(0, len(pzls), cols)]) if pzls else "IMPOSSIBLE")((lambda collections, sys: breadthFirstSearch(sys.argv[1].replace('_', ' '), collections.deque([[sys.argv[1].replace('_', ' ')]]), set([sys.argv[1].replace('_', ' ')])))(__import__("collections"), __import__("sys")), 10))
