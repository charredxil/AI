class template:
    def __init__(self, length):
        self.cells = length
        self.side = int(0.5 + length**0.5)
        self.boxheight, self.boxwidth = nearest_factors(self.side)
        self.generate_peerset()
    def _rcb(self, ix):
        r, c = divmod(ix, self.side)
        return r, c, self.boxheight*(r//self.boxheight) + c//self.boxwidth
    def generate_peerset(self):
        self.peers = []
        group = [[set() for _ in range(self.side)] for _ in range(3)]
        for ix in range(self.cells):
            nums = self._rcb(ix)
            for j in range(3): group[j][nums[j]].add(ix)
        for ix in range(self.cells):
            r, c, b = self._rcb(ix)
            self.peers.append(group[0][r].union(group[1][c]).union(group[2][b]) - {ix})
    def string(self, p):
        out = ''
        breakrow = (('+'+'-'*self.boxwidth)*self.boxheight)+'+\n'
        for ix, val in enumerate(p):
            r, c, b = self._rcb(ix)
            if c == 0 and r % self.boxheight == 0: out += breakrow
            if c % self.boxwidth == 0: out += '|'
            out += str(val) if val != '.' else ' '
            if c == self.side-1: out += '|\n'
        return out + breakrow[:-1]

class solver:
    def __init__(self, s, template):
        self.t = template
        self.board = list(s)
        self.value = values(s, self.t.side)
        self.conflicts = [[0 for _ in range(self.t.side)] for _ in range(self.t.cells)]
        self.ignore = set()
    def select(self, ix):
        val = self.value.index(self.board[ix])
        for cell in self.t.peers[ix]:
            self.conflicts[cell][val] += 1
            if self.board[cell] != '.': continue
            poss = None
            for num, count in enumerate(self.conflicts[cell]):
                if count == 0 and poss: break
                if count == 0: poss = self.value[num]
            else:
                self.board[cell] = poss
                self.select(cell)
    def deselect(self, ix):
        if ix in self.ignore or self.board[ix] == '.': return
        val = self.value.index(self.board[ix])
        self.ignore.add(ix)
        for cell in self.t.peers[ix]:
            self.conflicts[cell][val] -= 1
            if self.conflicts[cell][val] == 0:
                self.deselect(cell)
                self.board[cell] == '.'
        self.ignore.remove(ix)
    def solution(self):
        for i in range(self.t.cells):
            if self.board[i] != '.': self.select(i)
        self._solution(0)
        return self.board
    def _solution(self, ix):
        if ix == self.t.cells: return True
        if self.board[ix] != '.': return self._solution(ix+1)
        self.ignore.add(ix)
        for num in filter(lambda n: self.conflicts[ix][n] == 0, range(self.t.side)):
            self.board[ix] = self.value[num]
            self.select(ix)
            if self._solution(ix+1): return True
            self.deselect(ix)
            self.board[ix] = '.'
        return False

def nearest_factors(num):
    for mul in range(2, num+1):
        lo, hi = mul, num/mul
        if int(hi) != hi: continue
        if lo < hi: continue
        return (int(hi), lo)
def values(s, side):
    values = set()
    for ch in s:
        if ch != '.': values.add(ch)
    if len(values) == side: return list(values)
    cur = 49 if any(map(lambda v: 49 <= ord(v) <= 57, values)) else 65
    while len(values) < side:
        if 65 > cur > 57: cur = 65
        if chr(cur) in values: cur += 1
        else: values.add(chr(cur))
    return list(values)