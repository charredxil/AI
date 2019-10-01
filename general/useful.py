from collections import deque
from functools import partial
from heapq import heappop, heappush, heapify
from inspect import signature
from math import inf

def newfuncs(data, *funcs, should=1):
    newfuncs = []
    for f in funcs:
        if not f: 
            newfuncs.append(None)
            continue
        if len(signature(f).parameters) > should:
            newf = lambda *x, f=f: f(*x, data)
            newfuncs.append(newf)
        else:
            newfuncs.append(f)
    return tuple(newfuncs)

def flipbfs(root, goal, adjacents, impossible=None, data=None):
    if root == goal: return [root]
    imp, adj = newfuncs(data, impossible, adjacents)
    if imp and imp(root): return None
    prevs = [{}, {}]
    qs = [deque([root]), deque([goal])]
    f = 0
    while True:
        node = qs[f].popleft()
        for x in adj(node):
            if x in prevs[f] or x == root or x == goal: continue
            prevs[f][x] = node
            if x in prevs[1-f]:
                return path(x, prevs[0])[:-1] + path(x, prevs[1])[::-1]
            qs[f].append(x)
        f = 1 - f

def bfs(root, goal, adjacents, impossible=None, data=None):
    if root == goal: return [root]
    imp, adj = newfuncs(data, impossible, adjacents)
    if imp and imp(root): return None
    prev = {}
    q = deque([root])
    while True:
        node = q.popleft()
        for x in adj(node):
            if x in prev or x == root: continue
            prev[x] = node
            if x == goal: return path(x, prev)
            q.append(x)

def floodfill(root, adjacents, data=None):
    adj, = newfuncs(data, adjacents)
    vis = {root}
    q = [root]
    while q:
        node = q.pop()
        for x in adj(node):
            if x in vis: continue
            vis.add(x)
            q.append(x)
    return vis

def hfs(root, goal, adjacents, h, impossible=None, data=None):
    imp, adj = newfuncs(data, impossible, adjacents)
    if imp and imp(root): return None
    prev = {}
    q = [(h(root, data), root)]
    while True:
        dist, node = heappop(q)
        if node == goal: return path(node, prev)
        for x in adj(node):
            if x in prev or x == root: continue
            heappush(q, (h(x, data), x))
            prev[x] = node

def ffs(root, goal, adjacents, heur, impossible=None, data=None):
    imp, adj, h = newfuncs(data, impossible, adjacents, heur)
    if imp and imp(root): return None
    prev = {}
    q = [(h(root), 0, root)]
    while True:
        heur, dist, node = heappop(q)
        if node == goal: return path(node, prev)
        for x in adj(node):
            if x in prev or x == root: continue
            heappush(q, (h(x)+dist+1, dist+1, x))
            prev[x] = node

def flipastar(root, goal, adjacents, heur, cost=lambda *a: 1, impossible=None, rdata=None, gdata=None):
    imp, adj, gh, = newfuncs(gdata, impossible, adjacents, heur)
    cst, = newfuncs(gdata, cost, should=2)
    rh, = newfuncs(rdata, heur)
    h = [gh, rh]
    if imp and imp(root): return None
    prev = [{}, {}]
    g = [{root : 0}, {goal : 0}]
    op = [{root : h[0](root)}, {goal : h[1](goal)}]
    q = [[(op[0][root], root)], [(op[1][goal], goal)]]  
    cl = [set(), set()]
    f = 0
    while True:
        fval, node = heappop(q[f])
        for succ in adj(node):
            if succ in cl[1-f]: 
                return path(node, prev[0]) + path(node, prev[1])[::-1][1:]
            if succ in cl[f]: continue
            g[f][succ] = g[f][node] + cst(node, succ)
            newf = h[f](succ) + g[f][succ]
            if succ not in op[f] or newf < op[f][succ]:
                heappush(q[f], (newf, succ))
                op[f][succ] = newf
                prev[f][succ] = node
        if node in op[f]: del op[f][node]
        cl[f].add(node)
        f = 1-f

def astar(root, goal, adjacents, heur, cost=lambda *a: 1, impossible=None, data=None):
    imp, adj, h = newfuncs(data, impossible, adjacents, heur)
    cst, = newfuncs(data, cost, should=2)
    if imp and imp(root): return None

    prev = {}
    g = {root : 0} #node : distfromroot
    f = {root : h(root)} #node : f
    q = [(f[root], root)] #(f, node)
    cl = set()
    while q:
        fval, node = heappop(q)
        cl.add(node)
        for succ in adj(node):
            if succ == goal: return path(node, prev) + [goal]
            if succ in cl: continue
            newg = g[node] + cst(node, succ)
            newf = h(succ) + newg
            if succ not in g or newg < g[succ]:
                heappush(q, (newf, succ))
                g[succ] = newg
                f[succ] = newf
                prev[succ] = node

def idastar(root, goal, adjacents, heur, impossible=None, data=None):
    imp, adj, h = newfuncs(data, impossible, adjacents, heur)
    def search(g):
        node = path[-1]
        f = g + h(node)
        if f > bound: return f
        if node == goal: return -1
        mn = inf
        for succ in adj(node):
            if succ not in pathset:
                path.append(succ)
                pathset.add(succ)
                t = search(g + 1)
                if t == -1: return -1
                if t < mn: mn = t
                path.pop()
                pathset.remove(succ)
        return mn
    if imp(root): return None
    bound = h(root)
    path = [root]
    pathset = {root,}
    while True:
        t = search(0)
        if t == -1: return path
        bound = t
        #print(bound)

def path(cur, prev):
    path = [cur]
    while cur in prev and prev[cur] is not None:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return path
