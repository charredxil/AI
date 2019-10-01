from unionfind import unionfind
from collections import deque
class graph:
    def __init__(self, file, adjs=False, comps=False):
        self.wkeys = {}
        self.kwords = {}
        self.adjs = adjs
        self.comps = comps
        if(comps):
            self._uf = unionfind()
        self.edges = 0
        self.vertices = 0
        with open(file) as fin:
                for line in fin:
                    self.addword(line.strip())
                    self.vertices += 1
        if self.adjs: self.buildadjs()
        if self.comps:
            self.comps = self._uf.getsets()
    def buildadjs(self):
        self.adjs = {}
        for word in self.wkeys:
                ns = self.adjacents(word)
    def addword(self, word):
        self.wkeys[word] = set()
        if self.comps: tounion = [word]
        for ix in range(len(word)):
            key = word[:ix]+'_'+word[ix+1:]
            self.wkeys[word].add(key)
            if key in self.kwords:
                self.edges += len(self.kwords[key])
                if self.comps:
                    tounion.append(next(iter(self.kwords[key])))
                self.kwords[key].add(word)
            else:
                self.kwords[key] = {word,}
        if self.comps:
            self._uf.add(word)
            if len(tounion) > 1: self._uf.union(*tounion)
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
    def path(self, wordi, wordf):
        if wordi not in self.wkeys or wordf not in self.wkeys: return None
        if wordi == wordf: return [wordi]
        vis = {wordi,}
        q = deque([[wordi]])
        while q:
            past = q.popleft()
            for adj in self.adjacents(past[-1]):
                if adj in vis: continue
                newpast = past[:] + [adj]
                if adj == wordf: return newpast
                q.append(newpast)
                vis.add(adj)