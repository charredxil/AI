class sudoku:
    def __init__(self, s):
        self.size = int(0.5 + len(s)**0.5)
        self.boxheight, self.boxwidth = nearest_factors(self.size)
        self.values = set()
        for ch in s: 
            if ch != '.': self.values.add(ch)
        complete_values(self.values, self.size)
        self.opts = []
        self.solution = []
        for ix, ch in enumerate(s):
            if ch == '.':
                self.opts.append(domain(self.values))
                self.solution.append(None)
            else:
                self.opts.append(domain([ch]))
                self.solution.append(ch)
        self.saved = []
        self.generate_constraints()
    def prune(self):
        for var, val in enumerate(self.solution):
            if val is None: continue
            self.assign(var, val)
        changed = True
        while changed:
            changed = False
            for c in self.constraints:
                changed = changed or c.hyperarc_prune()
    def search(self):
        unsolved = list(filter(lambda x: not self.solution[x], range(self.size**2)))
        if not unsolved: 
            print('solved')
            return True
        to_assign = min(unsolved, key=lambda x: len(self.opts[x]))
        for choice in self.opts[to_assign].copy():
            success = self.assign(to_assign, choice, guess=True)
            if success and self.search(): return True
            if success: self.restoreall()
        self.solution[to_assign] = None
        return False
    def assign(self, var, val, guess=False):
        worked = []
        totalsuccess = True
        self.solution[var] = val
        for c in self.vconstrs[var]:
            success = c.propogate(var)
            if success: worked.append(c)
            else: 
                totalsuccess = False
                break
        if not totalsuccess:
            for c in reversed(worked): c.restoreall()
            self.solution[var] = None
            return False
        if guess: self.saved.append((var, worked))
        return True
    def restoreall(self):
        var, torestore = self.saved.pop()
        for c in reversed(torestore): c.restoreall()
        self.solution[var] = None
    def _rcb(self, var):
        r, c = divmod(var, self.size)
        b = self.boxheight*(r//self.boxheight) + c//self.boxwidth
        return r, c, b
    def generate_constraints(self):
        constraint_vars = {}
        for x in range(self.size):
            constraint_vars[('b', x)] = set()
            constraint_vars[('r', x)] = set()
            constraint_vars[('c', x)] = set()
        for x in range(self.size**2):
            r, c, b = self._rcb(x)
            if b==12: print(r, c, b)
            constraint_vars[('r', r)].add(x)
            constraint_vars[('c', c)].add(x)
            constraint_vars[('b', b)].add(x)
        self.vconstrs = [set() for _ in range(self.size**2)]
        self.constraints = []
        for ix, vs in enumerate(constraint_vars.values()):
            constr = alldiff(self, vs)
            self.constraints.append(constr)
            for v in vs: self.vconstrs[v].add(constr)
    def __str__(self):
        out = ''
        breakrow = (('+'+'-'*self.boxwidth)*self.boxheight)+'+\n'
        for ix, val in enumerate(self.solution):
            r, c, b = self._rcb(ix)
            if c == 0 and r % self.boxheight == 0:
                out += breakrow
            if c % self.boxwidth == 0: out += '|'
            out += str(val) if val else ' '
            if c == self.size-1: out += '|\n'
        return out + breakrow[:-1]

class alldiff:
    def __init__(self, sudoku, vs):
        self.su = sudoku
        self.vars = vs
        self.saved = []
    def hyperarc_prune(self):
        changed = set()
        for var in self.vars:
            if self.su.solution[var]: continue
            for val in self.su.opts[var].copy():
                self.su.solution[var] = val
                success = self.propogate(var, local=True)
                if not success or not self.locallypossible():
                    if success: self.restoreall()
                    self.su.opts[var].hide(val)
                    changed.add(var)
                else: self.restoreall()
            self.su.solution[var] = None
        for var in changed:
            if len(self.su.opts[var]) == 0: print('error')
            if len(self.su.opts[var]) == 1:
                #print('assigned', var, self.su.opts[var].getone())
                self.su.assign(var, self.su.opts[var].getone())
        return True if changed else False
    def locallypossible(self):
        unsolved = list(filter(lambda x: not self.su.solution[x], self.vars))
        if not unsolved: return True
        to_assign = min(unsolved, key=lambda x: len(self.su.opts[x]))
        for choice in self.su.opts[to_assign].copy():
            self.su.solution[to_assign] = choice
            success = self.propogate(to_assign, local=True)
            if success and self.locallypossible(): 
                self.restoreall()
                self.su.solution[to_assign] = None
                return True
            if success: self.restoreall()
        self.su.solution[to_assign] = None
        return False
    def saveall(self, exclude=set()):
        sav = set()
        for v in self.vars:
            if not self.su.solution[v] and v not in exclude:
                self.su.opts[v].save()
                sav.add(v)
        self.saved.append(sav)
    def restoreall(self):
        torestore = self.saved.pop()
        for v in torestore:
            self.su.opts[v].restore()
            if len(self.su.opts[v]) > 1:
                self.su.solution[v] = None
    def isseen(self, val, exclude=set()):
        for checkv in self.vars:
            if checkv in exclude: continue
            if self.su.solution[checkv] == val: return True
        return False
    def propogate(self, var, local=False):
        if self.isseen(self.su.solution[var], exclude={var}): return False
        self.saveall(exclude = {var})
        success = self._propogate(var, local)
        if not success:
            self.restoreall()
        return success
    def _propogate(self, var, local=False):
        su = self.su
        val = su.solution[var]
        for v in self.vars:
            if var == v or su.solution[v] or val not in su.opts[v]:
                continue
            su.opts[v].hide(val)
            if len(su.opts[v]) == 1:
                newval = su.opts[v].getone()
                if self.isseen(newval): return False
                if local:
                    su.solution[v] = newval
                    success = self.propogate(var, local)
                    if not success:
                        su.solution[v] = None
                        return False
                    for var in self.saved[-2]:
                        if var in self.saved[-1]:
                            self.su.opts[var]._pastlen.pop()
                    self.saved[-2] |= self.saved[-1]
                    self.saved.pop()
                else: 
                    success = su.assign(v, newval)
                    if not success: return False
        return True

class domain(set):
    def __init__(self, it):
        set.__init__(self, it)
        self._hidden = []
        self._pastlen = []
    def getone(self):
        return next(iter(self))
    def save(self):
        self._pastlen.append(len(self))
    def restore(self):
        diff = self._pastlen.pop() - len(self)
        if diff:
            self |= set(self._hidden[-diff:])
            del self._hidden[-diff:]
    def hide(self, val):
        set.remove(self, val)
        self._hidden.append(val)

def nearest_factors(num):
    for mul in range(2, num+1):
        lo, hi = mul, num/mul
        if int(hi) != hi: continue
        if lo < hi: continue
        return (int(hi), lo)
def complete_values(values, size):
    if len(values) == size: return
    cur = 65
    if any(map(lambda v: 49 <= ord(v) <= 57, values)):
        cur = 49
    while len(values) < size:
        if 65 > cur > 57: cur = 65
        if chr(cur) in values: cur += 1
        else: values.add(chr(cur))