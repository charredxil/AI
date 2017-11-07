import time
unit = [{0, 1, 2, 6, 7, 8}, {2, 3, 4, 8, 9, 10}, {5, 6, 7, 12, 13, 14}, {7, 8, 9, 14, 15, 16}, {9, 10, 11, 16, 17, 18}, {13, 14, 15, 19, 20, 21}, {15, 16, 17, 21, 22, 23}]
unitsof = [{0}, {0}, {0, 1}, {1}, {1}, {2}, {0, 2}, {0, 2, 3}, {0, 1, 3}, {1, 3, 4}, {1, 4}, {4}, {2}, {2, 5}, {2, 3, 5}, {3, 5, 6}, {3, 4, 6}, {4, 6}, {4}, {5}, {5}, {5, 6}, {6}, {6}]
row = [set(range(0, 5)), set(range(5, 12)), set(range(12, 19)), set(range(19, 24)), {3, 4, 10, 11, 18}, {1, 2, 8, 9, 16, 17, 23}, {0, 6, 7, 14, 15, 21, 22}, {5, 12, 13, 19, 20}, {1, 0, 6, 5, 12}, {3, 2, 8, 7, 13, 14, 19}, {4, 10, 9, 16, 15, 21, 20}, {11, 18, 17, 23, 22}]
rowsof = [{0, 6, 8}, {0, 5, 8}, {0, 5, 9}, {0, 4, 9}, {0, 4, 10}, {1, 7, 8}, {1, 6, 8}, {1, 6, 9}, {1, 5, 9}, {1, 5, 10}, {1, 4, 10}, {1, 4, 11}, {2, 7, 8}, {2, 7, 9}, {2, 6, 9}, {2, 6, 10}, {2, 5, 10}, {2, 5, 11}, {2, 4, 11}, {3, 7, 9}, {3, 7, 10}, {3, 6, 10}, {3, 6, 11}, {3, 5, 11}] 

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
        for r in rowsof[tofill]:
            for tri in row[r]:
                removeOpt(tri, num, removed)
        return removed
    #iterates through possible options
    for num in cellopts:
        solution[tofill] = str(num)
        print(''.join(solution))
        removed = removeInvalids(tofill, num)
        if solve(opts, solution, row_constr): return True
        for tri in removed: opts[tri].add(num)
    solution[tofill] = '.'
    opts[tofill] = cellopts
    return False

start = time.time()
row_constr = True
opts  = {x : set(range(1, 8 if row_constr else 7)) for x in range(24)}
solution = ['.' for _ in range(24)]
solve(opts, solution, row_constr)
print(time.time()-start)