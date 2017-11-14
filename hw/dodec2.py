import sys
adj = [{1,2,3,4,5},{0,2,5,6,10},{0,1,3,6,7},{0,2,4,7,8},{0,3,5,8,9},{0,4,1,9,10},{1,2,10,7,11},{2,3,6,8,11},{3,4,7,9,11},{4,5,8,10,11},{5,1,9,6,11},{6,7,8,9,10}]

question   = 2
size       = int(sys.argv[1])
numtocolor = 12 if question == 2 else size
numcolors  = 1  if question == 1 else size
opts       = [set(range(numcolors)) for _ in range(12)]
solution   = [None for _ in range(12)]
blank      = set(range(12))
def solve():
    if len(blank) == 12 - numtocolor: return True
    colorable = list(filter(lambda x: len(opts[x]) != 0, blank))
    if not colorable: return None
    face = min(colorable, key=lambda x: len(opts[x]))
    blank.remove(face)
    for color in opts[face]:
        solution[face] = color
        removed = []
        for a in adj[face]:
            if color not in opts[a]: continue
            opts[a].remove(color)
            removed.append(a)
        if solve(): return True
        for a in removed: opts[a].add(color)
    blank.add(face)

if solve(): print(solution)
else: print("IMPOSSIBLE")