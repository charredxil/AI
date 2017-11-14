import itertools as itr
class problem:
    def __init__(self):
        self.next_constr_name = 0
        self.var_domain  = {}
        self.constr_funcvars = {}
        self.var_constrs = {}
    def one_solution(self):
        unsolveds = []
        for var, domain in self.var_domain.items():
            if not domain: return False
            if len(domain) > 1: unsolveds.append(var)
        if not unsolveds: return True
        tosat = min(unsolveds, key=lambda x: len(self.var_domain[x]))
        vardomain = self.var_domain[tosat].copy()
        for val in vardomain:
            self.var_domain[tosat] = {val}
            print(val)
            removed = self.consist_var(tosat, {})
            if removed is None: continue
            #print(removed)
            if self.one_solution(): return True
            self._addback(removed)
        self.var_domain[tosat] = vardomain
        return False
    def consist(self, constr):
        func, vs = self.constr_funcvars[constr]
        removed = {}
        var_ix = []
        inp = list(vs)
        for ix, var in enumerate(inp):
            if len(self.var_domain[var]) == 1:
                inp[ix] = next(iter(self.var_domain[var]))
            else: var_ix.append((var, ix))
        lvars = len(var_ix)
        if lvars == 0 and not func(*tuple(inp)):
            return None
        if lvars > 2: return removed
        if lvars == 1:
            #node consistancy
            var, ix = var_ix[0]
            for val in self.var_domain[var]:
                inp[ix] = val
                if not func(*tuple(inp)):
                    #print(var, val)
                    self._addremoved(removed, var, val)
        if lvars == 2:
            #arc consistancy
            for ta, tb in itr.permutations(var_ix, r=2):
                a, aix, b, bix = *ta, *tb
                for aval in self.var_domain[a]:
                    inp[aix] = aval
                    arc_consistant = False
                    for bval in self.var_domain[b]:
                        inp[bix] = bval
                        if func(*tuple(inp)):
                            arc_consistant = True
                            break
                    if not arc_consistant:
                        #print(a, aval, b)
                        self._addremoved(removed, a, aval)
        for var in removed:
            for val in removed[var]:
                self.var_domain[var].remove(val)
        for var in list(removed.keys()):
            removed = self.consist_var(var, removed)
        return removed
    def consist_var(self, var, removed):
        for c in self.var_constrs[var]:
            rem = self.consist(c)
            if rem is None:
                self._addback(removed)
                return None
            for v in rem: self._addremoved(removed, v, rem[v], s=True)
        return removed
    def var(self, name, domain):
        self.var_constrs[name] = set()
        self.var_domain[name] = set(domain)
    def constraint(self, func, vs, name=None):
        if not name:
            name = self.next_constr_name
            self.next_constr_name += 1
        self.constr_funcvars[name] = (func, tuple(vs))
        for var in vs:
            self.var_constrs[var].add(name)
        self.consist(name)
    def _addremoved(self, removed, var, val, s=False):
        if var in removed: 
            if s: removed[var] |= val
            else: removed[var].add(val)
        else: 
            if s: removed[var] = val
            else: removed[var] = {val}
    def _addback(self, removed):
        for v in removed:
            self.var_domain[v] |= removed[v]