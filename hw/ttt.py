display = lambda b: print('\n'.join([b[x:x+3] for x in range(0, 9, 3)]))
mover = lambda b: 'X' if b.count('X') == b.count('O') else 'O'
other = lambda c: 'X' if c=='O' else 'O'
empties = lambda b: {i for i in range(9) if b[i] == '.'}
groups = [{*range(x, x+3)} for x in range(0, 9, 3)] + [{*range(x, 9, 3)} for x in range(3)] + [{0, 4, 8}, {2, 4, 6}]

def partition(b, mvr):
    for g in groups:
        if all([b[i] == other(mvr) for i in g]): return set(), {-1}, set()
        elif all([b[i] == mvr for i in g]): return {-1}, set(), set()
    empt = empties(b)
    if not empt: return set(), set(), {-1}
    good, bad, tie = set(), set(), set()
    for c in empt:
        newb = b[:c] + mvr + b[c+1:]
        _good, _bad, _tie = partition(newb, other(mvr))
        if _good: bad.add(c)
        elif _tie: tie.add(c)
        else: good.add(c)
    return good, bad, tie

import sys
b = sys.argv[1]
display(b)
mvr = mover(b)
print("{} to move".format(mvr), "Possible moves: "+str(empties(b)), sep='\n')
print(partition(b, mvr))
