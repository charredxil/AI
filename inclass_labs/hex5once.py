units = [{0, 1, 2, 6, 7, 8}, {2, 3, 4, 8, 9, 10}, {5, 6, 7, 12, 13, 14}, {7, 8, 9, 14, 15, 16}, {9, 10, 11, 16, 17, 18}, {13, 14, 15, 19, 20, 21}, {15, 16, 17, 21, 22, 23}]

labeluses = [0 for _ in range(6)]
def bruteForce(pzl, empty):
    if isInvalid(pzl): return None
    if not empty: return pzl
    tofill = next(iter(empty))
    empty.remove(tofill)
    choices = filter(lambda x: labeluses[x] < 4, range(6))
    if not empty:
        choices = filter(lambda x: labeluses[x] == 4, range(6))
    for num in sorted(choices, key=lambda x: labeluses[x]):
        labeluses[num] += 1
        pzl[tofill] = chr(65+num)
        print(''.join(pzl))
        bF = bruteForce(pzl, empty)
        if bF: return bF
        labeluses[num] -= 1
    pzl[tofill] = '.'
    empty.add(tofill)
def isInvalid(pzl):
    for g in units:
        seen = set()
        for cell in g:
            if pzl[cell] in seen: return True
            if pzl[cell] != '.': seen.add(pzl[cell])
    return False

empty = set(range(24))
pzl = ['.' for _ in range(24)]
bruteForce(pzl, empty)
print(labeluses)
