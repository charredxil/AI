class cell:
    def __init__(self):
        self.U = self.D = self.L = self.R = self
        self.H = None
        self.indices = None
class header(cell):
    def __init__(self, name):
        cell.__init__(self)
        self.size = 0
        self.name = name
class torus:
    def __init__(self, cols):
        self.H = header("H")
        self.nrows = self.ncols = 0
        self.col = []
        self.add_columns(cols)
    def add_columns(self, cnames):
        prev = self.H
        for cname in cnames:
            cur = header(cname)
            cur.indices = (-1, self.ncols)
            self.col.append(cur)
            prev.R, cur.L = cur, prev
            self.ncols += 1
            prev = cur
        prev.R = self.H
        self.H.L = prev
    def add_row(self, row):
        prev = None
        start = None
        for ix in sorted(row):
            cur = cell()
            cur.indices = (self.nrows, ix)
            if prev: prev.R, cur.L = cur, prev
            else: start = cur
            col = self.col[ix]
            cur.H = col
            col.size += 1
            last = col.U
            last.D, cur.U = cur, last
            col.U, cur.D = cur, col
            prev = cur
        start.L, cur.R = cur, start
        self.nrows += 1
    def min_col(self):
        col = self.H.R
        if col is self.H: return None
        mn = col
        while col is not self.H:
            if col.size < mn.size: mn = col
            col = col.R
        return mn
    def first_col(self):
        return self.H.R if self.H.R is not self.H else None
    def cover(self, col):
        col.R.L = col.L
        col.L.R = col.R
        possrow = col.D
        while possrow is not col:
            satcol = possrow.R
            while satcol is not possrow:
                satcol.D.U = satcol.U
                satcol.U.D = satcol.D
                satcol.H.size -= 1
                satcol = satcol.R
            possrow = possrow.D
    def uncover(self, col):
        possrow = col.U
        while possrow is not col:
            unsatcol = possrow.L
            while unsatcol is not possrow:
                unsatcol.H.size += 1
                unsatcol.D.U = unsatcol.U.D = unsatcol
                unsatcol = unsatcol.L
            possrow = possrow.U
        col.R.L = col.L.R = col

def solve(torus):
    sol = []
    return _solve(torus, sol)
def _solve(torus, solution):
    if torus.H.R is torus.H:
        yield solution.copy()
        return
    col = torus.min_col()
    torus.cover(col)
    row = col.D
    while row is not col:
        solution.append(row.indices[0])
        satcol = row.R
        while satcol is not row:
            torus.cover(satcol.H)
            satcol = satcol.R
        for s in _solve(torus, solution): yield s
        solution.pop()
        unsatcol = row.L
        while unsatcol is not row:
            torus.uncover(unsatcol.H)
            unsatcol = unsatcol.L
        row = row.D
    torus.uncover(col)



