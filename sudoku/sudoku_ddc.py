import sys, cProfile, time
from functools import reduce

class Deducer:
    def __init__(self, p, t):
        self.t = t
        self.board = ['.' for _ in range(self.t.cells)]
        self.vals = values(p, t.side)
        self.opts = {(0, i) : domain(self.vals.copy()) for i in range(t.cells)}
        self.opts.update({(1, val, unit) : domain(t.groups[unit].copy()) for val in self.vals for unit in range(t.side*3)})
        self.empty = domain(self.opts.keys())
        self.save = False
        self.saved = self.failed = None
        for ix, v in filter(lambda t: t[1] != '.', enumerate(p)): self.assign((0, ix), v)
    def sumopts(self): return sum(map(lambda x: len(x), self.opts.values()))
    def deduce(self):
        prev_sum_opts = self.sumopts()
        prev_ept = len(self.empty)
        loops = 0
        a = None
        while True:
            loops += 1
            self.deduce_noguess(prevalt=a)
            a = self.shave_deduce()
            #print(len(self.empty))
            new_sum_opts = self.sumopts()
            if new_sum_opts == prev_sum_opts: break
            prev_sum_opts = new_sum_opts
        print("deduction loops:", loops)
    def deduce_noguess(self, prevalt=None):
        prev_sum_opts = self.sumopts()
        if prevalt is None: a1, a2, a3 = self.empty.copy(), self.empty.copy(), self.empty.copy()
        else: a1, a2, a3 = prevalt.copy(), prevalt.copy(), prevalt.copy()
        while True:
            a1 = self.shareset_deduce(prevalt = a2 | a3)
            a2 = self.preempt_deduce(prevalt = a1 | a3)
            a3 = self.altpair_deduce(prevalt = a1 | a2)
            new_sum_opts = self.sumopts()
            if new_sum_opts == prev_sum_opts: break
            prev_sum_opts = new_sum_opts
    def shave_deduce(self):
        self.save = True
        for key in sorted(self.empty, key=lambda x:len(self.opts[x])):
            res = self.shave_deduce_key(key)
            if res[0]: return res[1]
            res = self.shave_deduce_key(key, fardeduce=True)
            if res[0]: return res[1]
        self.save = False
    def shave_deduce_key(self, key, fardeduce=False):
        if key not in self.empty: return
        toremove = set()
        self.empty.save()
        oldboard = self.board.copy()
        for choice in self.opts[key].copy():
            self.saved = set()
            self.failed = False
            self.assign(key, choice)
            if not self.failed and fardeduce: self.deduce_noguess()
            self.empty.restore(resave=True)
            self.board = oldboard.copy()
            for a in self.saved: self.opts[a].restore()
            if self.failed: toremove.add(choice)
            if len(self.opts[key]) - len(toremove) == 1: break
        alt = set()
        for o in toremove: alt |= self.removeopt(key, o)
        return (True, alt) if toremove else (False, alt)
    def shareset_deduce(self, prevalt=None):
        if not self.empty: return set()
        toremove = {}
        groups = reduce(lambda a, b: a | b, (self.keygroups(a) for a in prevalt)) if prevalt else range(self.t.cells*3)
        for g in groups:
            for val in self.vals:
                if (1, val, g) not in self.empty: continue
                shared = reduce(lambda a, b: a & b, [self.t.cellgroups[ix] for ix in self.opts[(1, val, g)]]) - {g}
                if len(shared) == 0: continue
                shared = list(shared)[0]
                for ix in (self.t.groups[shared] - self.opts[(1, val, g)]):
                    if ix in toremove: toremove[ix].add(val)
                    else: toremove[ix] = {val}
        alt = set()
        for ix in toremove:
            for val in toremove[ix]:
                alt |= self.removeassign(ix, val)
        return alt
    def altpair_deduce(self, prevalt=None):
        if not self.empty: return set()
        alt = set()
        vals = {k[1] for k in prevalt if k[0] == 1} if prevalt else self.vals
        for val in vals: alt |= self.altpair_deduce_val(val)
        return alt
    def altpair_deduce_val(self, val):
        altpairs = {}
        for g in range(self.t.side*3):
            if len(self.opts[(1, val, g)]) == 2:
                pair = tuple(self.opts[(1, val, g)])
                for ix, c in enumerate(pair):
                    if c in altpairs: altpairs[c].add(pair[1-ix])
                    else: altpairs[c] = {pair[1-ix]}
        toremovefrom = set()
        uncolored = set(altpairs.keys())
        fail = None
        def color(ix, c, c_opp):
            if ix in c_opp: fail = c_opp
            elif ix not in c:
                c.add(ix)
                for a in altpairs[ix]: color(a, c_opp, c)
        while uncolored:
            tocolor = next(iter(uncolored))
            c1, c2 = set(), set()
            color(tocolor, c1, c2)
            uncolored -= (c1 | c2)
            if fail: toremovefrom |= fail
            else:
                c1peers = reduce(lambda a, b: a | b, [self.t.peers[i] for i in c1])
                c2peers = reduce(lambda a, b: a | b, [self.t.peers[i] for i in c2])
                toremovefrom |= c1peers & c2peers
        alt = set()
        for ix in toremovefrom: alt |= self.removeassign(ix, val)
        return alt
    def preemptive_sets(self, keys):
        partial = {frozenset(): 0}
        total = []
        for o in map(lambda k: frozenset(self.opts[k]), keys):
            new_partial = {}
            for s, count in partial.items():
                new = o | s
                if new in partial: partial[new] = max(partial[new], count+1)
                else: new_partial[new] = count+1
                if len(new) == count+1: total.append(new)
            partial.update(new_partial)
        return total
    def keygroups(self, k): return {k[2]} if k[0] else self.t.cellgroups[k[1]]
    def preempt_deduce(self, prevalt=None):
        if not self.empty: return set()
        prevaltg = reduce(lambda a, b: a | b, (self.keygroups(k) for k in prevalt)) if prevalt else range(self.t.side*3)
        deducable = {(0, x) for x in prevaltg} | {(1, x) for x in prevaltg}
        alt = set()
        while deducable:
            typ, gx = next(iter(deducable))
            deducable.remove((typ, gx))
            keys = {(1, val, gx) for val in self.vals} if typ else {(0, c) for c in self.t.groups[gx]} 
            keys &= self.empty
            presets = self.preemptive_sets(keys)
            upgroups = set()
            for preset in presets:
                for k in keys:
                    if not self.opts[k] <= preset:
                        for o in preset: 
                            a = self.removeopt(k, o)
                            alt |= a
                            for k in a: upgroups.update(self.keygroups(k))
            deducable.update({(typ, ug) for ug in upgroups})
        return alt
    def assign(self, key, onlyopt):
        altered = set()
        if key in self.empty:
            ix, val = (onlyopt, key[1]) if key[0] else (key[1], onlyopt)
            self.board[ix] = val
            if len(self.opts[key]) != 1:
                if self.save and key not in self.saved: 
                    self.saved.add(key)
                    self.opts[key].save()
                for o in self.opts[key].copy():
                    if o != onlyopt: self.opts[key].hide(o)
            self.empty.hide((0, ix))
            for group in self.t.cellgroups[ix]:
                for v in (self.vals - {val}): 
                    altered.update(self.removeopt((1, v, group), ix))
                self.empty.hide((1, val, group))
            for cell in self.t.peers[ix]:
                altered.update(self.removeassign(cell, val))
        return altered
    def removeopt(self, key, opt):
        altered = set()
        if opt in self.opts[key]:
            altered.add(key)
            if self.save and key not in self.saved: 
                self.saved.add(key)
                self.opts[key].save()
            self.opts[key].hide(opt)
            lenopts = len(self.opts[key])
            if self.save and lenopts == 0: self.failed = True
            if lenopts == 1:
                onlyopt = next(iter(self.opts[key]))
                altered.update(self.assign(key, onlyopt))
        return altered
    def removeassign(self, ix, val):
        altered = self.removeopt((0, ix), val)
        for group in self.t.cellgroups[ix]:
            altered |= self.removeopt((1, val, group), ix)
        return altered

def solve(p, t):
    d = Deducer(p, t)
    #print("#opts pre-deduce:", sum(map(lambda x: len(x), d.opts.values())))
    d.deduce_noguess()
    #print("#opts post-deduce:", sum(map(lambda x: len(x), d.opts.values())))
    #print("Valid" if check(d.board, t) else "Invalid")
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
        self.boxheight, self.boxwidth = nearest_factors(self.side)
        self.groups = [set() for _ in range(self.side*3)]
        for ix in range(self.cells):
            for k, g in enumerate(self._rcb(ix)): self.groups[k*self.side+g].add(ix)
        self.cellgroups = [{k for k in range(len(self.groups)) if i in self.groups[k]} for i in range(self.cells)]
        self.peers = [reduce(lambda a, b: a | b, [self.groups[k] for k in self.cellgroups[i]]) - {i} for i in range(self.cells)]
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
        self._hidden = []
        self._pastlen = []
    def save(self):
        self._pastlen.append(len(self))
    def restore(self, resave=False):
        pl = self._pastlen[-1] if resave else self._pastlen.pop()
        diff = pl - len(self)
        if diff != 0:
            self.update(self._hidden[-diff:])
            del self._hidden[-diff:]
    def hide(self, val):
        if val not in self: return
        self.remove(val)
        if self._pastlen: self._hidden.append(val)

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
    for g in t.groups:
        seen = set()
        for cell in g:
            if p[cell] == '.': continue
            if p[cell] in seen: return False
            seen.add(p[cell])
    return True

if __name__ == "__main__": main()