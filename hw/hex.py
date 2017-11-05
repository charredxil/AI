unit    = [{0, 1, 2, 6, 7, 8}, {2, 3, 4, 8, 9, 10}, {5, 6, 7, 12, 13, 14}, {7, 8, 9, 14, 15, 16}, {9, 10, 11, 16, 17, 18}, {13, 14, 15, 19, 20, 21}, {15, 16, 17, 21, 22, 23}]
row     = [set(range(0, 5)), set(range(5, 12)), set(range(12, 19)), set(range(19, 24))]
unitsof = [{0}, {0}, {0, 1}, {1}, {1}, {2}, {0, 2}, {0, 2, 3}, {0, 1, 3}, {1, 3, 4}, {1, 4}, {4}, {2}, {2, 5}, {2, 3, 5}, {3, 5, 6}, {3, 4, 6}, {4, 6}, {4}, {5}, {5}, {5, 6}, {6}, {6}]
rowof   = [0]*5 + [1]*7 + [2]*7 + [3]*5
def solve(opts, empty, rc):
    if not empty: return True
    tofill = min(empty, key=lambda x: len(opts[x]))
    empty.remove(tofill)
    for num in opts[tofill]:
        removed = {tofill : opts[tofill].copy()}
        opts[tofill] = {num}
        for u in unitsof[tofill]:
            for tri in unit[u]:
                if num in opts[tri]:
                    opts[tri].remove(num)
                    removed[tri] = num
        if rc:
            for tri in row[rowof[tofill]]:
                if num in opts[tri]:
                    opts[tri].remove(num)
                    removed[tri] = num
        if solve(opts, empty, rc): return True
        for tri in removed:
            for n in removed[tri]: opts[tri].add(n)
    return False
rc = True
opts  = [set(range(1, 8 if rc else 7)) for _ in range(24)]
empty = set(range(24))
print(solve(opts, empty, rc))