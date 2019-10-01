import sys, time, cProfile, itertools
from functools import reduce
class Deducer:
    def __init__(self, p, t):
        self.t = t
        self.board = ['.' for _ in range(self.t.cells)]
        self.vals = values(p, t.side)
        self.opts = {(0, i) : domain(self.vals) for i in range(t.cells)}
        self.opts.update({(1, val, unit) : domain(t.groupcells[unit]) for val in self.vals for unit in range(t.groups)})
        self.empty = domain(self.opts.keys())
        self.savedkeys = set()
        self.saving = False
        self.fail = False
        for c, v in filter(lambda t: t[1] != '.', enumerate(p)): self.assign(c, v)
    def deduce(self, alts=None, guess=True):
        funcs = [self.shareset_deduce, self.preempt_deduce, self.altpair_deduce]
        if guess: funcs.append(self.shave_deduce)
        altf = []
        allalts = set()
        while True: 
            for ix, f in enumerate(funcs):
                if ix >= len(altf): altf.append(f(alts=alts))
                else: altf[ix] = f(alts=altf[ix])
                if not altf[ix]: continue
                for a in altf: a |= altf[ix]
                allalts |= altf[ix]
                break
            else: break
        return allalts
    def search(self, guess=False):
        self.saving = True
        self.deduce(guess=guess)
        self._search(guess=guess)
    def _search(self, guess=False):
        if not self.empty: return True
        key = min(self.empty, key=lambda k: len(self.opts[k]))
        for opt in self.opts[key].copy():
            self.fail = False
            self.savedkeys = set()
            self.empty.save()
            oldboard = self.board.copy()
            cell, val = (opt, key[1]) if key[0] else (key[1], opt)
            alts = self.assign(cell, val)
            if not self.fail: self.deduce(alts=alts, guess=guess)
            savedkeys = self.savedkeys.copy()
            if not self.fail and self._search(): return True
            self.empty.restore()
            for sk in savedkeys: self.opts[sk].restore()
            self.board = oldboard
        return False
    def shave_deduce(self, alts=None):
        if not self.empty: return set()
        oldsav = self.saving
        self.saving = True
        altcount = {}
        shaveable = alts if alts else self.empty
        for k in sorted(shaveable, key=lambda k: len(self.opts[k])):
            for o in self.opts[k].copy():
                self.savedkeys = set()
                self.empty.save()
                oldboard = self.board.copy()
                cell, val = (o, k[1]) if k[0] else (k[1], o)
                newalts = self.assign(cell, val)
                if not self.fail: newalts |= self.deduce(alts=newalts, guess=False)
                if not self.fail and not self.empty: 
                    self.saving = oldsav
                    return set()
                self.empty.restore()
                for sk in self.savedkeys: self.opts[sk].restore()
                self.board = oldboard
                if self.fail: 
                    self.saving = oldsav
                    self.fail = False
                    return self.removeassign(cell, val)
                else: altcount[(k, o)] = newalts
        self.saving = oldsav
        self.fail = False
    def altpair_deduce(self, alts=None):
        if not self.empty: return set()
        def color(i, altpairs, c=set(), c_opp=set()):
            if i not in c:
                c.add(i)
                for a in altpairs[i]: c_opp, c = color(a, altpairs, c_opp, c)
            return c, c_opp
        vals = self.vals if not alts else {k[1] for k in alts if k[0]}
        alt = set()
        for v in vals:
            altpairs = {}
            for g in range(self.t.groups):
                if len(self.opts[(1, v, g)]) == 2:
                    pair = tuple(self.opts[(1, v, g)])
                    for ix, c in enumerate(pair):
                        if c in altpairs: altpairs[c].add(pair[1-ix])
                        else: altpairs[c] = {pair[1-ix]}
            uncolored = set(altpairs.keys())
            while uncolored:
                tocolor = uncolored.pop()
                c1, c2 = color(tocolor, altpairs, set(), set())
                uncolored -= c1|c2
                c1peers = reduce(lambda a, b: a | b, [self.t.peers[i] for i in c1])
                c2peers = reduce(lambda a, b: a | b, [self.t.peers[i] for i in c2])
                for ix in (c1peers & c2peers): alt |= self.removeassign(ix, v)
        return alt
    def preempt_deduce(self, alts=None, limit=5):
        if not self.empty: return set()
        groups = range(self.t.groups) if not alts else self.keygroups(alts)
        newalts = set()
        for typ, g in ({(0, g) for g in groups} | {(1, g) for g in groups}):
            keys = ({(1, val, g) for val in self.vals} if typ else {(0, c) for c in self.t.groupcells[g]}) & self.empty
            curlimit = min(limit, len(keys)-1)
            partial, count, length = [], [], []
            totals = []
            for o in map(lambda k: self.opts[k], keys):
                olen = len(o)
                if olen > curlimit: continue
                exactadded = False
                for ix, s in enumerate(partial[:]):
                    if o <= s:
                        count[ix] += 1
                        if count[ix] == length[ix]: 
                            totals.append(s)
                        exactadded = True
                    else:
                        new = s | o
                        newlen = len(new)
                        if newlen > curlimit: continue
                        partial.append(new)
                        count.append(count[ix]+1)
                        length.append(newlen)
                if not exactadded:
                    partial.append(set(o))
                    count.append(1)
                    length.append(olen)
            for s in totals:
                for k in keys:
                    if self.opts[k] <= s: continue
                    for o in s:
                        newalts |= self.removeopt(k, o, allrem=True)
        return newalts
    def shareset_deduce(self, alts=None):
        if not self.empty: return set()
        newalts = set()
        tosearch = None
        if alts is None: tosearch = itertools.product(self.vals, range(self.t.groups))
        else: tosearch = {k[1:] for k in alts if k[0]}
        for v, g in tosearch:
            if (1, v, g) not in self.empty: continue
            shared = reduce(lambda a, b: a & b, [self.t.cellgroups[c] for c in self.opts[(1, v, g)]]) - {g}
            if len(shared) == 0: continue
            for c in (self.t.groupcells[next(iter(shared))] - self.opts[(1, v, g)]):
                newalts |= self.removeassign(c, v)
        return newalts
    def keygroups(self, keys):
        gs = set()
        for k in keys: gs |= {k[2]} if k[0] else self.t.cellgroups[k[1]]
        return gs
    def removeopt(self, key, opt, allrem=False):
        if self.fail: return set()
        if allrem:
            c, v = (opt, key[1]) if key[0] else (key[1], opt)
            return self.removeassign(c, v)
        elif key in self.empty and opt in self.opts[key]:
            self.savehide(key, opt)
            alts = {key}
            if len(self.opts[key]) == 1:
                onlyopt = next(iter(self.opts[key]))
                cell, val = (onlyopt, key[1]) if key[0] else (key[1], onlyopt)
                alts |= self.assign(cell, val)
            elif self.saving and len(self.opts[key]) == 0: self.fail = True
            return alts
        return set()
    def assign(self, cell, val):
        alts = set()
        if self.fail: return alts
        if self.board[cell] == '.':
            self.board[cell] = val
            self.savesetto((0, cell), {val})
            self.empty.hide((0, cell))
            for c in self.t.peers[cell]: 
                alts |= self.removeassign(c, val)
            for g in self.t.cellgroups[cell]:
                if self.fail: return alts
                self.savesetto((1, val, g), {cell})
                self.empty.hide((1, val, g))
                for v in (self.vals - {val}):
                    alts |= self.removeopt((1, v, g), cell)
        elif self.board[cell] != val: self.fail = True
        return alts
    def removeassign(self, cell, val):
        alts = set()
        if self.fail: return alts
        if self.board[cell] == '.':
            alts |= self.removeopt((0, cell), val)
            if not alts: return alts
            for group in self.t.cellgroups[cell]:
                alts |= self.removeopt((1, val, group), cell)
        return alts
    def savehide(self, k, v):
        if self.saving and k not in self.savedkeys:
            self.opts[k].save()
            self.savedkeys.add(k)
        self.opts[k].hide(v)
    def savesetto(self, k, vs):
        if self.saving and k not in self.savedkeys:
            self.opts[k].save()
            self.savedkeys.add(k)
        if not self.opts[k].setto(vs): self.fail = True
    def __str__(self): return self.t.string(''.join(self.board))

def solve(p, t):
    d = Deducer(p, t)
    d.search(guess=False)
    print("Valid" if check(d.board, t) else "Invalid")
    return ''.join(d.board)
def main():
    filename = 'puzzles.txt' if len(sys.argv) == 1 else sys.argv[1]
    puzzles = [line.strip() for line in open(filename)]
    template_size = {}
    start = time.time()
    for ix, p in enumerate(puzzles, start=1):
        if len(p) not in template_size: template_size[len(p)] = template(len(p))
        t = template_size[len(p)]
        print('Puzzle #{}:'.format(ix))
        psolved = solve(p, t)
        print(t.string(p, psolved))
    print("Elapsed time:", time.time()-start)

class template:
    def __init__(self, length):
        self.cells = length
        self.side = int(0.5 + length**0.5)
        self.groups = self.side*3
        self.boxheight, self.boxwidth = nearest_factors(self.side)
        self.groupcells = [set() for _ in range(self.groups)]
        for ix in range(self.cells):
            for k, g in enumerate(self._rcb(ix)): self.groupcells[k*self.side+g].add(ix)
        self.cellgroups = [{k for k in range(self.groups) if i in self.groupcells[k]} for i in range(self.cells)]
        self.peers = [reduce(lambda a, b: a | b, [self.groupcells[k] for k in self.cellgroups[i]]) - {i} for i in range(self.cells)]
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
class domain(set):
    def __init__(self, it):
        set.__init__(self, it)
        self.hidden = []
        self.pastlen = []
    def setto(self, vals):
        if not vals <= self: return False
        for v in (self - vals): self.hide(v)
        return True
    def hide(self, val):
        if val not in self: return
        self.remove(val)
        if self.pastlen: self.hidden.append(val)
    def save(self):
        self.pastlen.append(len(self))
    def restore(self):
        dif = self.pastlen.pop() - len(self)
        if dif == 0: return
        self.update(self.hidden[-dif:])
        del self.hidden[-dif:]

def nearest_factors(num):
    for mul in range(2, num+1):
        lo, hi = mul, num/mul
        if int(hi) != hi: continue
        if lo < hi: continue
        return (int(hi), lo)
def values(s, side):
    values = set(s) - {'.'}
    for ch in "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0":
        if len(values) == side: return values
        if ch not in values: values.add(ch)
def check(p, t):
    for g in range(t.groups):
        seen = set()
        for cell in t.groupcells[g]:
            if p[cell] == '.': continue
            if p[cell] in seen: return False
            seen.add(p[cell])
    return True

if __name__ == "__main__": main()