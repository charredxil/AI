import sys
sys.path.append('A:/')
import useful as u

class graph:
    def __init__(self, file, adjs=False, comps=False):
        self.wkeys = {}
        self.kwords = {}
        self.adjs = adjs
        self.comps = comps
        self.edges = 0
        self.vertices = 0
        with open(file) as fin:
                for line in fin:
                    self.addword(line.strip())
                    self.vertices += 1
        if self.adjs: self.buildadjs()
        if self.comps: self.buildcomps()
    def buildcomps(self):
        self.comps = []
        vxs = set(self.wkeys.keys())
        x=0
        while len(vxs):
            r = next(iter(vxs))
            vis = u.floodfill(r, self.adjacents)
            for n in vis:
                vxs.remove(n)
            self.comps.append(vis)
    def buildadjs(self):
        self.adjs = {}
        for word in self.wkeys:
                ns = self.adjacents(word)
    def addword(self, word):
        self.wkeys[word] = set()
        for ix in range(len(word)):
            key = word[:ix]+'_'+word[ix+1:]
            self.wkeys[word].add(key)
            if key in self.kwords:
                self.edges += len(self.kwords[key])
                self.kwords[key].add(word)
            else:
                self.kwords[key] = {word,}
    def adjacents(self, word):
        if self.adjs and word in self.adjs:
            return self.adjs[word]
        n = {word,}
        if word in self.wkeys:
            for key in self.wkeys[word]:
                n |= self.kwords[key]
        n.remove(word)
        if not self.adjs: self.adjs = {}
        self.adjs[word] = n
        return n
    def commons(self, wordi, wordf):
        com = 0
        for ix, val in enumerate(wordi):
            com += (wordf[ix] == val)
        return com
    def path(self, wordi, wordf):
        imp = lambda x: x not in self.wkeys
        return u.astar(wordi, wordf, self.adjacents, self.commons, impossible=imp, data=wordf)
    def path2(self, wordi, wordf):
        imp = lambda x: x not in self.wkeys
        return u.bfs(wordi, wordf, self.adjacents, impossible=imp)

def _path(cur, prev):
    path = [cur]
    while cur in prev and prev[cur] is not None:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return path