from collections import Iterator
class exactcovers(Iterator):
    def __init__(self, row, col):
        self.poss = row
        self.cond = col
        self.unsat = set(self.cond)
        self.it = self._solve()
        self.partial = []
    def __next__(self): return next(self.it)
    def _solve(self):
        if not self.unsat:
            yield self.partial.copy()
            return
        choice = min(self.unsat, key=lambda x: len(self.cond[x]))
        for p in list(self.cond[choice]):
            self._select(p)
            for sol in self._solve(): yield sol
            self._deselect(p)
    def _select(self, p):
        self.partial.append(p)
        for sat_cond in self.poss[p]:
            self.unsat.remove(sat_cond)
            for useless_poss in self.cond[sat_cond]:
                for c in self.poss[useless_poss]:
                    if c != sat_cond: self.cond[c].remove(useless_poss)
    def _deselect(self, p):
        self.partial.pop()
        for unsat_cond in self.poss[p]:
            self.unsat.add(unsat_cond)
            for useful_poss in self.cond[unsat_cond]:
                for c in self.poss[useful_poss]:
                    if c != unsat_cond: self.cond[c].add(useful_poss)
    


