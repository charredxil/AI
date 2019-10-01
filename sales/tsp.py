from collections import namedtuple
from math import pi, acos, sin, cos, inf
import random
import time
import itertools as it
from tkinter import *

Location = namedtuple("Location", "long lat")
Point = namedtuple("Point", "x y")

### Helper Functions ###

def get_locations(file_name):
    locs = []
    with open(file_name) as f:
        for line in list(f)[1:]:
            lg, lt = map(lambda s: float(s)/1000, line.split())
            locs.append(Location(lg, lt))
    return locs

def flat_coords(locs, width, height, margin):
    coords = {}
    minlong = minlat = 361.0
    maxlong = maxlat = -1
    for loc in locs:
        lat = loc.lat if loc.lat > 0 else 360 + loc.lat
        long = loc.long if loc.long > 0 else 360 + loc.long
        minlat = min(lat, minlat); maxlat = max(lat, maxlat)
        minlong = min(long, minlong); maxlong = max(long, maxlong)
        coords[loc] = Point(long, lat)
    latv = minlat if maxlat - minlat <= 180 else maxlat
    longv = minlong if maxlong - minlong <= 180 else maxlong
    latr = maxlat - minlat if maxlat - minlat <= 180 else 360 + minlat - maxlat
    longr = maxlong - minlong if maxlong - minlong <= 180 else 360 + minlong - maxlong
    conv = min(((height - 2*margin)/latr), ((width - 2*margin)/longr))
    for loc, pt in coords.items():
        y = ((pt.y - latv) % 360) * conv + (height - latr*conv)/2
        x = ((pt.x - longv) % 360) * conv + (width - longr*conv)/2
        coords[loc] = Point(x, height-y)
    return coords

def globedist(a, b):
    R = 6371
    conv = pi/180.0
    y1 = a.lat * conv
    x1 = a.long * conv
    y2 = b.lat * conv
    x2 = b.long * conv
    return acos(sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(x2-x1)) * R

### Classes (Glorified Structs) ###

class Map:
    def __init__(m, locs, width=1000, height=600, margin=25, edge_color='red', edge_width=1, node_color='black', node_width=None):
        m.locs = locs
        m.locset = frozenset(m.locs)
        m.width = width
        m.height = height
        m.margin = margin
        m.edge_id = {}
        m.node_id = {}
        m.coords = flat_coords(m.locs, m.width, m.height, m.margin)
        m.root = Tk()
        m.canvas = Canvas(m.root, width=m.width, height=m.height, bg='white')
        m.canvas.pack()
        ###
        m.reconfig(edge_color, edge_width, node_color, node_width)
    def loc_show(m, *ns):
        r = m.node_width
        for n in ns:
            id = None
            if n in m.node_id: id = m.node_id[n]
            if id is None and n in m.locset:
                x, y = m.coords[n]
                id = m.canvas.create_oval(x-r, y-r, x+r, y+r, fill=m.node_color)
                m.node_id[n] = id
    def cycle_show(m, cyc):
        to_del = set()
        to_add = set()
        for e in cycle_edges(cyc):
            to_add.add(e)
        for e in m.edge_id:
            if e in to_add: to_add.remove(e)
            else: to_del.add(e)
        for e in to_add:
            a, b = tuple(e)
            id = m.canvas.create_line(*m.coords[a], *m.coords[b], fill=m.edge_color, width=m.edge_width)
            m.canvas.tag_lower(id)
            m.edge_id[e] = id
        for e in to_del:
            m.canvas.delete(m.edge_id[e])
            m.edge_id.pop(e)
        m.loc_show(*cyc)
        m.root.update()
    def reconfig(m, edge_color='red', edge_width=1, node_color='black', node_width=None):
        m.edge_color = edge_color
        m.edge_width = edge_width
        m.node_color = node_color
        m.node_width = node_width if node_width else edge_width*2
        for n, id in m.node_id.items():
            m.canvas.delete(id)
            m.node_id[n] = None
        m.loc_show(*m.node_id.keys())
        for id in m.edge_id.values():
            m.canvas.itemconfig(id, fill=edge_color, width=edge_width)

class UnionFind:
    def __init__(self, n):
        self._id = list(range(n))
        self._sz = [1] * n
    def _root(self, i):
        j = i
        while (j != self._id[j]):
            self._id[j] = self._id[self._id[j]]
            j = self._id[j]
        return j
    def find(self, p, q):
        return self._root(p) == self._root(q)
    def union(self, p, q):
        i = self._root(p)
        j = self._root(q)
        if (self._sz[i] < self._sz[j]):
            self._id[i] = j
            self._sz[j] += self._sz[i]
        else:
            self._id[j] = i
            self._sz[i] += self._sz[j]

class CGraph:
    def __init__(c, n, edge_weight):
        c.n = n
        c.nodes = [*range(n)]
        c._weight = {}
        c._edge_weight = edge_weight
    def weight(c, *xs):
        e = xs[0] if len(xs) == 1 else edge(*xs)
        if e not in c._weight:
            c._weight[e] = c._edge_weight(e)
        return c._weight[e]

class MGraph:
    def __init__(g, n, edge_weight):
        g.n = n
        g.nodes = [*range(n)]
        g.edges = {}
        g.adj = {n:{} for n in g.nodes}
        g._weight = {}
        g._edge_weight = edge_weight
    def weight(g, *xs):
        e = xs[0] if len(xs) == 1 else edge(*xs)
        if e not in g._weight:
            g._weight[e] = g._edge_weight(e)
        return g._weight[e]
    def add_edge(g, e):
        a, b = tuple(e)
        if e in g.edges:
            g.edges[e] += 1
            g.adj[a][e] += 1
            g.adj[b][e] += 1
        else:
            g.edges[e] = 1
            a, b = tuple(e)
            g.adj[a][e] = 1
            g.adj[b][e] = 1
    def remove_edge(g, e):
        a, b = tuple(e)
        if e in g.edges:
            g.edges[e] -= 1
            g.adj[a][e] -= 1
            g.adj[b][e] -= 1
            if g.edges[e] == 0:
                g.edges.pop(e)
                g.adj[a].pop(e)
                g.adj[b].pop(e)

### Graph and Cycle Helper Methods ###

def edge(*xs):
    xs = xs[0] if len(xs) == 1 else xs
    return frozenset(xs)
def cycle_edges(cyc):
    return map(edge, zip(cyc, cyc[-1:] + cyc[:-1]))
def cycle_weight(c, cyc):
    return sum(map(c.weight, cycle_edges(cyc)))
def cycle_reorder(cyc):
    ix0 = cyc.index(0) if 0 in cyc else None
    if ix0 is None: return []
    cyc = cyc[ix0:] + cyc[:ix0]
    if cyc[1] > cyc[-1]:
        cyc = cyc[:1] + [*reversed(cyc[1:])]
    return cyc

### Travelling Salesman Algorithms ###

tsp_callback = None

def tsp_greedy(c, cyc=None):
    root = 639 % c.n
    cyc = [root]
    unvis = set(c.nodes) - {root}
    while unvis:
        minloc, mindist = None, inf
        for loc in unvis:
            dist = c.weight(cyc[-1], loc)
            if dist < mindist:
                minloc, mindist = loc, dist
        cyc.append(minloc)
        unvis.remove(minloc)
    tsp_callback(cyc)
    return cyc

def uncross(cyc, i, k):
    return cyc[0:i] + [*reversed(cyc[i:k+1])] + cyc[k+1:]
def tsp_2opt(c, cyc=None):
    cyc = cyc if cyc else tsp_greedy(c)
    best_weight = cycle_weight(c, cyc)
    count = 0
    while True:
        improved = False
        for d in range(c.n//2, 0, -1):
            for i in range(0, c.n):
                k = (i+d) % c.n
                if k < i: i, k = (k+1), (i-1)
                k_1 = (k+1) % c.n
                old_eweight = c.weight(cyc[i-1], cyc[i]) + c.weight(cyc[k], cyc[k_1])
                new_eweight = c.weight(cyc[i-1], cyc[k]) + c.weight(cyc[i], cyc[k_1])
                if new_eweight < old_eweight:
                    cyc = uncross(cyc, i, k)
                    best_weight = best_weight + (new_eweight - old_eweight)
                    improved = True
                    count += 1
                    if count % 5 == 0: tsp_callback(cyc)
        if not improved: break
    tsp_callback(cyc)
    return cyc

def fuse_segments(c, *segments, init_weight=0):
    seg0 = segments[0]
    free_end = seg0[-1]
    best_weight = init_weight
    if init_weight == 0:
        for seg in segments[1:]:
            best_weight += c.weight(free_end, seg[0])
            free_end = seg[-1]
        best_weight += c.weight(free_end, seg0[0])
        init_weight = best_weight
    best_cyc = None
    for order in it.permutations(segments[1:]):
        for flip in range(0, 2**(len(segments)-1)):
            free_end = seg0[-1]
            weight = 0
            for e, seg in enumerate(order):
                if flip & (1 << e):
                    weight += c.weight(free_end, seg[-1])
                    free_end = seg[0]
                else:
                    weight += c.weight(free_end, seg[0])
                    free_end = seg[-1]
            weight += c.weight(free_end, seg0[0])
            if weight + 0.000001 < best_weight:
                best_weight = weight
                best_cyc = seg0.copy()
                for e, seg in enumerate(order):
                    if flip & (1 << e):
                        best_cyc.extend(reversed(seg))
                    else:
                        best_cyc.extend(seg)
    return (init_weight - best_weight), best_cyc
def tsp_3opt(c, cyc=None):
    cyc = cyc if cyc else tsp_greedy(c)
    best_weight = cycle_weight(c, cyc)
    count = 0
    while True:
        init_count = count
        for i in range(0, c.n):
            for j in range(i+1, c.n):
                for k in range(j+1, c.n):
                    reduction, better_cyc = fuse_segments(c, (cyc[k:] + cyc[0:i]), cyc[i:j], cyc[j:k])
                    if better_cyc is not None:
                        best_weight = best_weight - reduction
                        cyc = better_cyc
                        print("IMPROVEMENT:", reduction, "km")
                        count += 1
                        if count % 5 == 0: tsp_callback(cyc)
        if count == init_count: break
    tsp_callback(cyc)
    return cyc

def tsp_permute(c, cyc=None):
    cyc = cyc if cyc else tsp_greedy(c)
    p = 8
    for i in range(c.n - p):
        seg = cyc[i:i+p]
        min_weight = sum(map(c.weight, [*cycle_edges(seg)][1:]))
        min_seg = seg
        for mid in it.permutations(seg[1:-1]):
            if len(mid) != p-2: continue
            new_seg = seg[:1] + list(mid) + seg[-1:]
            weight = sum(map(c.weight, [*cycle_edges(new_seg)][1:]))
            if weight < min_weight:
                min_seg = new_seg
                min_weight = weight
        cyc = cyc[:i] + min_seg + cyc[i+p:]
    print(cyc)
    tsp_callback(cyc)
    return cyc

def tsp_christofides(c, cyc=None, root=None):
    UF = UnionFind(c.n)
    G = MGraph(c.n, c._edge_weight)
    for a, b in sorted(filter(lambda t: t[0] != t[1], it.product(c.nodes, repeat=2)), key=c.weight):
        if not UF.find(a, b):
            G.add_edge(edge(a, b))
            UF.union(a, b)
    G_odd = {n for n in G.nodes if len(G.adj[n]) % 2}
    while G_odd:
        x = G_odd.pop()
        y = min(G_odd, key=lambda y: c.weight(x, y))
        G_odd.remove(y)
        G.add_edge(edge(x, y))
    unfinished = set()
    circ = []
    root = root if root is not None else 683 % G.n
    while True:
        part_circ = [root]
        if not circ: circ = [root]
        while len(part_circ) == 1 or part_circ[-1] != root:
            end = part_circ[-1]
            e = next(iter(G.adj[end]))
            _a, _b = tuple(e)
            nxt = _a if _b == end else _b
            G.remove_edge(e)
            for n in (end, nxt):
                if len(G.adj[n]) == 0: unfinished.discard(n)
                else: unfinished.add(n)
            part_circ.append(nxt)
        ix_root = circ.index(root)
        circ = circ[:ix_root] + part_circ[:-1] + circ[ix_root:]
        if circ[0] == circ[-1]: circ = circ[:-1]
        if not unfinished: break
        root = next(iter(unfinished))
    visit = set()
    cyc = []
    for n in circ:
        if n in visit: continue
        visit.add(n)
        cyc.append(n)
    tsp_callback(cyc)
    return cyc


### I/O and Click Handling ###

cyc, m, c = None, None, None
def press_one(e):
    global cyc, m, c
    m.canvas.bind_all("<Key>", press_two)
    cyc = tsp_2opt(c, cyc)
    m.reconfig(edge_color='blue')
    print(', '.join(map(str, cycle_reorder(cyc))))
    print(cycle_weight(c, cyc), 'km')
def press_two(e):
    global cyc, m, c
    m.canvas.bind_all("<Key>", press_three)
    cyc = tsp_3opt(c, cyc)
    m.reconfig(edge_color='green')
    print(', '.join(map(str, cycle_reorder(cyc))))
    print(cycle_weight(c, cyc), 'km')
def press_three(e):
    global cyc, m, c
    m.root.destroy()

def main():
    global tsp_callback, cyc, m, c
    file_name = sys.argv[1] if len(sys.argv) > 1 else "KAD.txt"
    locs = get_locations(file_name)
    m = Map(locs)
    tsp_callback = lambda cyc: m.cycle_show([*map(lambda n: locs[n], cyc)])
    edge_weight = lambda e: (lambda t: globedist(locs[t[0]], locs[t[1]]))(tuple(e))
    c = CGraph(len(locs), edge_weight)

    m.canvas.bind_all("<Key>", press_one)
    m.root.lift()
    cyc = tsp_christofides(c)
    print(', '.join(map(str, cycle_reorder(cyc))))
    print(cycle_weight(c, cyc), 'km')
    m.root.mainloop()

if __name__ == "__main__": main()
