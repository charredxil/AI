import math, itertools, sys
sys.path.append('A:/')
import useful as u
class friend_graph:
    def __init__(self, n):
        self.size = n
        self.squares = set(itertools.takewhile(lambda x: x <= 2*n-1, (g**2 for g in range(1, n+1))))
        self.adjs = {k : set() for k in range(1, n+1)}
        for i in range(1, n+1):
            for j in range(1, n+1):
                if i+j in self.squares and i != j:
                    self.adjs[i].add(j)
                    self.adjs[j].add(i)
        self.components()
    def adjacents(self, node):
        return self.adjs[node]
    def components(self):
        v = set(range(1, self.size+1))
        self.comps = []
        while v:
            r = next(iter(v))
            vis = u.floodfill(r, self.adjacents)
            v = v - vis
            self.comps.append(vis)
    def ham(self):
        def simplifya():
            todelete = []
            for node in poss:
                if len(poss[node]) + cons[node] > 2: continue
                for s in poss[node]:
                    if (s, node) in edges: continue
                    edges.add((node, s))
                    cons[s] += 1
                    cons[node] += 1
                    todelete.append((node, s))
            for a, b in todelete:
                poss[a].remove(b)
                poss[b].remove(a)
        def simplifyb():
            for node in poss:
                if cons[node] != 1 or len(poss[node]) == 0: continue
                for 
        cons = {}
        edges = set()
        poss = {}
        for n in self.adjs:
            poss[n] = self.adjs[n].copy()
            cons[n] = 0
        for x in range(10):
            simplify()
        print(cons)

g = friend_graph(int(sys.argv[1]))
g.ham()
#print(g.adjs)