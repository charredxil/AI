import sys
seq = [int(s) for s in sys.argv[1:]]
arth = list(set(seq))
arth.sort()
flag, fore, back = True, True, True
for x in range(2, len(arth)):
    if arth[x] - arth[x-1] != arth[x-1] - arth[x-2]: flag = False
prev = None
for x in seq:
    if flag == False: break
    if prev and (arth.index(prev) + 1) % len(arth) == arth.index(x) and fore: back = False
    elif prev and (arth.index(prev) - 1) % len(arth) == arth.index(x) and back: fore = False
    elif prev: flag = False
    prev = x
print("YES" if flag else "NO")
