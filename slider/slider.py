from argparse import Namespace
import sys, math
from random import sample
from collections import deque
sys.path.append('A:/')
import useful as u

#heuristics
def manhattan(sl, data):
    pos = data.pos
    cols = data.cols
    md = 0
    for x in range(len(sl)):
        if sl[x] == ' ': continue
        yr, yc = pos[sl[x]]
        delta = abs(yr - x//cols) + abs(yc - x%cols)
        md += delta
    return md
def linearconflict(sl, data):
    def conflicts(line, linenum, vert=False):
        conf = 0
        for ix, ch1 in enumerate(line):
            if ch1 == ' ': continue
            rc1 = pos[ch1]
            for ch2 in line[ix+1:]:
                if ch2 == ' ': continue
                rc2 = pos[ch2]
                if rc2[vert] == rc1[vert] == linenum and rc2[1-vert] < rc1[1-vert]:
                    conf += 1
        return conf
    cols, pos = data.cols, data.pos
    lc = 0
    for x in range(cols):
        r = sl[x*cols:(x+1)*cols]
        c = sl[x::cols]
        lc += 2*conflicts(r, x)
        lc += 2*conflicts(c, x, vert=True)
    return lc + manhattan(sl, data)

#impossibility testing
def inversions(sl, data):
    cols, ixd = data.cols, data.ixd
    ic = 0
    for ix, x in enumerate(sl):
        if x == ' ': continue
        for iy, y in enumerate(sl[ix+1:], ix+1):
            if y == ' ' or ixd[y] >= ixd[x]: continue
            ic += 1
    return ic
def rowdiff(sl, data):
    cols = data.cols
    ixi = sl.index(' ')
    ixg = data.ixd[' ']
    return abs(ixi//cols - ixg//cols)
def impossible(sl, data):
    cols = data.cols
    icp = inversions(sl, data) % 2
    if cols % 2 == 1: return icp
    else: return icp ^ (rowdiff(sl, data) % 2)

#adjacency
def adjacents(sl, data):
    cols = data.cols
    _ix = sl.index(' ')
    ns = []
    def swapstr(s, i, j):
        if i < j: return s[:i] + s[j] + s[i+1:j] + s[i] + s[j+1:]
        else: return s[:j] + s[i] + s[j+1:i] + s[j] + s[i+1:]
    def addNewState(_new):
        newpzl = swapstr(sl, _ix, _new)
        ns.append(newpzl)
    for _new in data.lu[_ix]:
        addNewState(_new)
    return ns

#create data
ccount = lambda sl: int(math.sqrt(len(sl)))
def getdata(goal):
    data = {'str': goal}
    cols = ccount(goal)
    data['cols'] = cols
    data['ixd'] = {goal[ix] : ix for ix in range(len(goal))}
    data['pos'] = {goal[ix] : (ix//data['cols'], ix%data['cols']) for ix in range(len(goal))}
    v = ''
    for x in range(cols):
        v += goal[x::cols]
    data['str_v'] = v
    data['ixd_v'] = {data['str_v'][ix] : ix for ix in range(len(data['str_v']))}
    data['lu'] = {}
    for ix in range(len(goal)):
        data['lu'][ix] = set()
        if ix % cols != cols-1: data['lu'][ix].add(ix+1)
        if ix % cols != 0: data['lu'][ix].add(ix-1)
        if ix + cols < cols**2: data['lu'][ix].add(ix+cols)
        if ix - cols >= 0: data['lu'][ix].add(ix-cols)
    return Namespace(**data)

#makes a random puzzle
def randompzl(cols, solvable=None, goal=None):
    from random import shuffle
    b = []
    g = goal
    if not goal:
        init = ord('A')
        while len(b) < cols ** 2 - 1:
            b.append(chr(init+len(b)))
        b.append(' ')
        g = ''.join(b)
    else: b = list(goal)
    shuffle(b)
    i = ''.join(b)
    if solvable is None: ret = i
    elif impossible(i, getdata(g)) ^ solvable: ret = i
    else: ret = i[1]+i[0]+i[2:] if i.index(' ') >= 2 else i[:-2]+i[-1]+i[-2]
    return (ret, g)

#solve methods
def flipbfs(sl, goal):
    return u.flipbfs(sl, goal, adjacents, impossible, getdata(goal))
def bfs(sl, goal):
    return u.bfs(sl, goal, adjacents, impossible, getdata(goal))
def hfs(sl, goal, h):
    return u.hfs(sl, goal, adjacents, h, impossible, getdata(goal))
def ffs(sl, goal, h):
    return u.ffs(sl, goal, adjacents, h, impossible, getdata(goal))
def astar(sl, goal, h):
    return u.astar(sl, goal, adjacents, h, impossible=impossible, data=getdata(goal))
def flipastar(sl, goal, h):
    return u.flipastar(sl, goal, adjacents, h, impossible=impossible, gdata=getdata(goal), rdata=getdata(sl))
def idastar(sl, goal, h):
    return u.idastar(sl, goal, adjacents, h, impossible=impossible, data=getdata(goal))

#methods for quiz
def distribution(goal, getboards=False):
    data = getdata(goal)
    d = {0 : 1}
    if getboards: d = {0 : [goal]}
    vis = {goal,}
    q = deque([(goal, 0)])
    while q:
        node, dist = q.popleft()
        for x in adjacents(node, data):
            if x in vis: continue
            if getboards:
                if dist+1 in d: d[dist+1].append(x)
                else: d[dist+1] = [x]
            else:
                if dist+1 in d: d[dist+1] += 1
                else: d[dist+1] = 1
            vis.add(x)
            q.append((x, dist+1))
    return d
def anydifby1(sl, data):
    for ix, ch in enumerate(sl):
        n = ord(ch)
        for iy in data.lu[ix]:
            if abs(ord(sl[iy])-n) == 1: return True
    return False
def find1(root):
    data = getdata(root)
    vis = {root}
    q = deque([root])
    while q:
        node = q.popleft()
        for x in adjacents(node, data):
            if x in vis: continue
            if not anydifby1(x, data): return x
            vis.add(root)
            q.append(x)
    return vis
def difpos(a, b):
    for ix in range(len(a)):
        if a[ix] == b[ix]: return False
    return True

#pretty-prints a puzzle array
def pstring(sls, cols=1, moves=False, pr=False):
    out = []
    rnum = cnum = ccount(sls[0])
    rows = [sls[x:x+cols] for x in range(0, len(sls), cols)]
    for row in rows:
        rowout = []
        for x in range(rnum):
            rowout.append("  ".join([sl[x*cnum:(x+1)*cnum] for sl in row]))
        out.append('\n'.join(rowout))
    if moves: out.append("{} Moves".format(len(sls)-1))
    final = '\n\n'.join(out)
    if pr: print(final)
    return final