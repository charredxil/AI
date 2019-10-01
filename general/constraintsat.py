class problem:
    def __init__(self):
        self.vdomain   = {}
        self.vconstrs  = {}
        self.cfuncvars = {}
        self._nxtname  = 0
    def variable(self, var, vals):
        self.vdomain[var]  = domain(vals)
        self.vconstrs[var] = []
    def constraint(self, func, vs, name=None):
        if not name:
            name = self._nxtname
            self._nxtname += 1
        self.cfuncvars[name] = (func, vs)
        for v in vs:
            self.vconstrs[v].append(name)
        if len(vs) == 1: 

        
class constraint():
    def __init__(func):
        self.func = func
    def __call__(prob, partial):
        for
class domain(list):
    def __init__(self, it):
        list.__init__(self, it)
        self.hidden = []
        self.states  = []
    def save(self):
        self.states.append(len(self))
    def restore(self):
        numhid = self.states.pop()-len(self)
        if numhid:
            self.extend(self.hidden[-numhid:])
            del self.hidden[-numhid:]
    def hide(self, val):
        list.remove(self, val)
        self.hidden.append(val)



