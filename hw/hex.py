unit    = [{0, 1, 2, 6, 7, 8}, {2, 3, 4, 8, 9, 10}, {5, 6, 7, 12, 13, 14}, {7, 8, 9, 14, 15, 16}, {9, 10, 11, 16, 17, 18}, {13, 14, 15, 19, 20, 21}, {15, 16, 17, 21, 22, 23}]
row     = [set(range(0, 5)), set(range(5, 12)), set(range(12, 19)), set(range(19, 24))]
unitsof = [{0}, {0}, {0, 1}, {1}, {1}, {2}, {0, 2}, {0, 2, 3}, {0, 1, 3}, {1, 3, 4}, {1, 4}, {4}, {2}, {2, 5}, {2, 3, 5}, {3, 5, 6}, {3, 4, 6}, {4, 6}, {4}, {5}, {5}, {5, 6}, {6}, {6}]
rowof   = [0]*5 + [1]*7 + [2]*7 + [3]*5

def solve(opts, solution, row_constr):
    #if no more cells to fill, we have a solution
    if not opts: return True
    tofill = min(opts, key=lambda x: len(opts[x]))
    cellopts = opts.pop(tofill)
    #function removes invalid options
    def removeInvalids(tofill, num, removed=set()):
        def removeOpt(tri, num, removed):
            if tri != tofill and tri in opts and num in opts[tri]:
                opts[tri].remove(num)
                removed.add(tri)
        for u in unitsof[tofill]:
            for tri in unit[u]:
                removeOpt(tri, num, removed)
        if not row_constr: return removed
        for tri in row[rowof[tofill]]:
            removeOpt(tri, num, removed)
        return removed
    #iterates through possible options
    for num in cellopts:
        solution[tofill] = str(num)
        print(''.join(solution))
        removed = removeInvalids(tofill, num)
        if solve(opts, solution, row_constr): return True
        for tri in removed: opts[tri].add(num)
    opts[tofill] = cellopts
    return False

row_constr = True
opts  = {x : set(range(1, 8 if row_constr else 7)) for x in range(24)}
solution = ['.' for _ in range(24)]
solve(opts, solution, row_constr)
print(''.join(solution))