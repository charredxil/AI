import math, sys, time
sys.path.append('A:/')
import general.exactcover as ec

def exactcover(su, findall=True):
    solved_board = [[None for _ in range(su.size)] for _ in range(su.size)]
    satisfied_conds = set()
    conditions = {}
    possibilities = {}
    for rnum, row in enumerate(su.board):
        for cnum, val in enumerate(row):
            bnum = su.boxnum(rnum, cnum)
            if not val: continue
            solved_board[rnum][cnum] = val
            conds = cond_strs(rnum, cnum, bnum, val)
            for cond in conds: satisfied_conds.add(cond)
    for rnum, row in enumerate(su.board):
        for cnum, val in enumerate(row):
            bnum = su.boxnum(rnum, cnum)
            if val: continue
            for val in su.values:
                conds = cond_strs(rnum, cnum, bnum, val)
                poss = (rnum, cnum, val)
                if any(map(lambda x: x in satisfied_conds, conds)):
                    continue
                possibilities[poss] = conds
                for cond in conds:
                    if cond in conditions: conditions[cond].add(poss)
                    else: conditions[cond] = set([poss])
    solutions = ec.exactcovers(possibilities, conditions)
    if not solutions: return None
    for r, c, v in next(solutions): solved_board[r][c] = v
    return sudoku(solved_board, su.values)
    
class sudoku:
    def __init__(self, board, values, boxdims=None):
        self.board = board
        self.values = values
        self.size = len(board)
        self.boxheight, self.boxwidth = nearest_factors(self.size)
    def boxnum(self, r, c):
        return self.boxwidth*(r//self.boxheight) + c//self.boxwidth
    def __str__(self):
        out = ''
        breakrow = (('+'+'-'*self.boxwidth)*self.boxheight)+'+\n'
        for rnum, row in enumerate(self.board):
            if rnum % self.boxheight == 0:
                out += breakrow
            for cnum, val in enumerate(row):
                if cnum % self.boxwidth == 0: out += '|'
                out += str(val) if val else ' '
            out += '|\n'
        return out + breakrow[:-1]

cond_strs = lambda r, c, b, v: [(0, r, c), (1, r, v), (2, c, v), (3, b, v)]
def nearest_factors(num):
    for mul in range(2, num+1):
        lo, hi = mul, num/mul
        if int(hi) != hi: continue
        if lo < hi: continue
        return (int(hi), lo)
def makesudoku(s, blanks):
    values = set()
    size = int(math.sqrt(len(s)))
    board = [[None for _ in range(size)] for _ in range(size)]
    for i, ch in enumerate(s):
        if ch in blanks: continue
        board[i//size][i%size] = ch
        values.add(ch)
    if len(values) < len(board): complete_values(values, board)
    return sudoku(board, values)
def complete_values(values, board):
    cur = 65
    if any(map(lambda v: 49 <= ord(v) <= 57, values)): cur = 49
    while len(values) < len(board):
        if 65 > cur > 57: cur = 65
        if chr(cur) in values: cur += 1
        else: values.add(chr(cur))
