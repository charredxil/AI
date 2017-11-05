class queenboard:
    def __init__(self, n):
        self.n = n
        self.cdomain = [set(range(n)) for _ in range(n)]
        self.unplaced = set(range(n))
        self.solution = [None for _ in range(n)]
    def solve(self):
        if not self.unplaced: return True
        toplace = min(self.unplaced, key=lambda q: len(self.cdomain[q]))
        self.unplaced.remove(toplace)
        for col in self.cdomain[toplace]:
            removed = self.select(toplace, col)
            if self.solve(): return True
            self.deselect(toplace, removed)
        self.unplaced.add(toplace)
    def select(self, toplace, col):
        self.solution[toplace] = col
        removed = {}
        for qr in self.unplaced:
            removed[qr] = list(filter(lambda qc: self.conflict(toplace, qr, col, qc), self.cdomain[qr]))
        for qr in removed:
            for qc in removed[qr]: self.cdomain[qr].remove(qc)
        return removed
    def deselect(self, toplace, removed):
        self.solution[toplace] = None
        for qr in removed:
            for qc in removed[qr]: self.cdomain[qr].add(qc)
    def conflict(self, r1, r2, c1, c2):
        return c1 == c2 or abs(r1-r2) == abs(c1-c2)
    def __str__(self):
        out = ''
        template = '.'*self.n+'\n'
        for row in range(self.n):
            rowstr = template
            if self.solution[row] is not None:
                col = self.solution[row]
                rowstr = rowstr[:col] + 'Q' + rowstr[col+1:]
            out += rowstr
        return out

            