import sys, time, cProfile
sys.path.append('A:/')
import general.dlx as dlx

class template:
    def __init__(self, length):
        self.cells = length
        self.side = int(0.5 + length**0.5)
        self.boxheight, self.boxwidth = nearest_factors(self.side)
    def _rcb(self, ix):
        r, c = divmod(ix, self.side)
        return r, c, self.boxheight*(r//self.boxheight) + c//self.boxwidth
    def _string(self, p):
        out = '┌' + (('─'*self.boxwidth+'┬')*self.boxheight)[:-1] + '┐\n'
        breakrow = '├' + (('─'*self.boxwidth+'┼')*self.boxheight)[:-1] + '┤\n'
        row = [str(p[x:x+self.side]) for x in range(0, self.cells, self.side)]
        rowpipe = ['│'+'│'.join([r[x:x+self.boxwidth] for x in range(0, self.side, self.boxwidth)])+'│\n' for r in row]
        out += breakrow.join([''.join(rowpipe[x:x+self.boxheight]) for x in range(0, self.side, self.boxheight)])
        return out + '└' + (('─'*self.boxwidth+'┴')*self.boxheight)[:-1] + '┘\n'
    def string(self, *ps):
        xps = [''.join(map(lambda c: ' ' if c == '.' else c, p)) for p in ps]
        lines = [self._string(p).splitlines() for p in xps]
        return ''.join([' '.join(ls)+'\n' for ls in zip(*lines)])[:-1]

def solution(pz, t):
    vals = values(pz, t.side)
    condset = {(j, a, v) for j in range(1, 4) for a in range(t.side) for v in vals} | {(0, a, b) for a in range(t.side) for b in range(t.side)}
    possdict, poss = {}, []
    for x, v in filter(lambda t: t[1] != '.', enumerate(pz)): condset -= cond_names(*t._rcb(x), v)
    conds = list(condset)
    revconds = {cond : ix for ix, cond in enumerate(conds)}
    for x in filter(lambda x: pz[x] == '.', range(t.cells)):
        for v in vals: 
            cns = cond_names(*t._rcb(x), v)
            if any(map(lambda x: x not in condset, cns)): continue
            possdict[(x, v)] = [revconds[c] for c in cns]
    torus = dlx.torus(conds)
    for xv, lst in possdict.items():
        poss.append(xv)
        torus.add_row(lst)
    for sol in dlx.solve(torus):
        solvedpz = list(pz)
        for possx in sol:
            ix, v = poss[possx]
            solvedpz[ix] = v
        yield ''.join(solvedpz)

cond_names = lambda r, c, b, v: {(0, r, c), (1, r, v), (2, c, v), (3, b, v)}
def nearest_factors(num):
    for mul in range(2, num+1):
        lo, hi = mul, num/mul
        if int(hi) != hi: continue
        if lo < hi: continue
        return (int(hi), lo)
def values(s, side):
    values = set(s) - {'.'}
    for ch in "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if len(values) == side: return values
        if ch not in values: values.add(ch)
def main():
    filename = 'puzzles.txt' if len(sys.argv) == 1 else sys.argv[1]
    puzzles = [line.strip() for line in open(filename)]
    template_size = {}
    start = time.time()
    for ix, p in enumerate(puzzles, start=1):
        if len(p) not in template_size: template_size[len(p)] = template(len(p))
        t = template_size[len(p)]
        print('Puzzle #{}:'.format(ix))
        #print(len(list(solution(p, t))))
        psolved = next(solution(p, t))
        print(t.string(p, psolved))
    print("Elapsed time:", time.time()-start)
if __name__ == "__main__": main()