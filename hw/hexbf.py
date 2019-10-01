units = [{0, 1, 2, 6, 7, 8}, {2, 3, 4, 8, 9, 10}, {5, 6, 7, 12, 13, 14}, {7, 8, 9, 14, 15, 16}, {9, 10, 11, 16, 17, 18}, {13, 14, 15, 19, 20, 21}, {15, 16, 17, 21, 22, 23}]
rows = [{0, 1, 2, 3, 4}, {5, 6, 7, 8, 9, 10, 11}, {12, 13, 14, 15, 16, 17, 18}, {19, 20, 21, 22, 23}, {3, 4, 10, 11, 18}, {1, 2, 8, 9, 16, 17, 23}, {0, 6, 7, 14, 15, 21, 22}, {5, 12, 13, 19, 20}, {1, 0, 6, 5, 12}, {3, 2, 8, 7, 13, 14, 19}, {4, 10, 9, 16, 15, 21, 20}, {11, 18, 17, 23, 22}]

row_constr = False #set to False for Q1, True for Q2
groups = rows + units if row_constr else units
def bruteForce(pzl, empty):
    if isInvalid(pzl): return None
    if not empty: return pzl
    tofill = next(iter(empty))
    empty.remove(tofill)
    for num in range(1, 8 if row_constr else 7):
        pzl[tofill] = str(num)
        print(''.join(pzl))
        bF = bruteForce(pzl, empty)
        if bF: return bF
    pzl[tofill] = '.'
    empty.add(tofill)
def isInvalid(pzl):
    for g in groups:
        seen = set()
        for cell in g:
            if pzl[cell] in seen: return True
            if pzl[cell] != '.': seen.add(pzl[cell])
    return False

empty = set(range(24))
pzl = ['.' for _ in range(24)]
bruteForce(pzl, empty)
