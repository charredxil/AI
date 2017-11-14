import sys
adj = [{1, 4, 6}, {0, 2, 8}, {1, 3, 10}, {2, 4, 12}, {3, 0, 14}, {14, 6, 15}, {5, 7, 0}, {6, 8, 16}, {7, 9, 1}, {8, 10, 17}, {9, 11, 2}, {10, 12, 18}, {11, 13, 3}, {12, 14, 19}, {13, 5, 4}, {16, 19, 5}, {15, 17, 7}, {16, 18, 9}, {17, 19, 11}, {18, 15, 13}]

numtocolor = 20
numcolors  = 3
opts       = [set(range(numcolors)) for _ in range(20)]
solution   = ['.' for _ in range(20)]
blank      = set(range(20))
def solve():
    if len(blank) == 20 - numtocolor: return True
    colorable = list(filter(lambda x: len(opts[x]) != 0, blank))
    if not colorable: return None
    face = min(colorable, key=lambda x: len(opts[x]))
    blank.remove(face)
    for color in opts[face]:
        solution[face] = chr(65+color)
        removed = []
        for a in adj[face]:
            if color not in opts[a]: continue
            opts[a].remove(color)
            removed.append(a)
        if solve(): return True
        for a in removed: opts[a].add(color)
    blank.add(face)

if solve(): print(''.join(solution))
else: print("IMPOSSIBLE")