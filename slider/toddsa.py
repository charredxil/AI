def p(s):
    print(s[0:4])
    print(s[4:8])
    print(s[8:12])
    print(s[12:])
    print("")

def create(puzz, check):
    #closed set, child-parent
   seenmov = {puzz: ""}
   hist = {puzz: ""}
    #list of states and moves away
   movaway = {puzz: 0, "":0}
   popcount = 0
   improv = 0
   count = 0
   open = {}
   seen = set()
   seen.add(puzz)
   h = []
   l = check
   boo3 = True
   while(boo3):
       if (boo2):
           heappush(h, (distance(puzz, check), puzz))
           open[puzz] = 0
           while (len(h) > 0):
               vert = heappop(h)
               #print(vert)
               popcount += 1
               mov = moves(vert[1])
               for f in mov:
                   hist[f] = vert[1]
                   count = count + 1
                   if (f == check):
                       print("Popcount:" + str(popcount))
                       print("Number in closed set:" + str(len(seenmov)))
                       print("Number in open set:" + str(len(h)))
                       print("Improvements:" + str(improv))
                       seenmov[vert[1]] = hist[vert[1]]
                       seenmov[f] = hist[f]
                       return seenmov
                   if (not (f in seenmov)):
                       movaway[f] = movaway[vert[1]] + 1
                       est = distance(f, check)+movaway[f]
                       #seenmov[f] = vert[1]
                       if not(f in open):
                        heappush(h, (est,f))
                        open[f] = est
                       elif est < open[f]:
                           improv = improv + 1
                           for q in range(0, len(h)):
                               if(h[q][1] == f):
                                   del h[q]
                                   break
                           heappush(h, (est, f))
               seenmov[vert[1]] = hist[vert[1]]
                       #print(movaway[f])
"""
def create(puzz, check):
    openset = []
    closedset = {}
    revclosedset = {}
    movaway = {puzz: 0}
    est = {}
    popcount = 0
    heappush(openset, (distance(puzz, check), puzz))
    est[puzz] = distance(puzz, check)
    while (True):
        v = heappop(openset)
        popcount += 1
        mov = moves(v[1])
        for suc in mov:
            if (suc == check):
                print("Popcount:" + str(popcount))
                return closedset
            if (suc in closedset):
                print("checkerino")
            else:
                # differnt "+1" for other cases
                f = distance(suc, check) + movaway[v[1]] + 1
                movaway[suc] = movaway[v[1]] + 1
                if not suc in openset:
                    heappush(openset, (f, suc))
                    est[suc] = f
                elif f < est[suc]:
                    heappush(openset, (f, suc))
        closedset[v] = est[v[1]]
"""
def moves(st):
    arr = []
    temp = ""
    matrix = []
    matrix.append(st[0:4])
    matrix.append(st[4:8])
    matrix.append(st[8:12])
    matrix.append(st[12:])
    for r in range(0, 4):
        for c in range(0, 4):
            if (matrix[r][c] == " "):
                index = 4 * r + c
                if (r != 0):
                    temp = st
                    temp = temp[:index - 4] + temp[index] + temp[index - 3:index] + temp[index - 4] + temp[
                                                                                                      index + 1:]
                    arr.append(temp)
                if (r != 3):
                    temp = st
                    temp = temp[:index] + temp[index + 4] + temp[index + 1:index + 4] + temp[index] + temp[
                                                                                                      index + 5:]
                    arr.append(temp)
                if (c != 0):
                    temp = st
                    temp = temp[:index - 1] + temp[index] + temp[index - 1] + temp[index + 1:]
                    arr.append(temp)
                if (c != 3):
                    temp = st
                    temp = temp[:index] + temp[index + 1] + temp[index] + temp[index + 2:]
                    arr.append(temp)
    return arr


def distance(s1, s2):
    summ = 0
    for y in s1:
        if(not(y==" ")):
            summ = summ + man(s1.index(y), s2.index(y))
    return summ


def man(f, s):
    return abs((f % 4) - (s % 4)) + abs((f // 4) - (s // 4))


def inv(strr):
    if (strr.index(" ") < len(strr) - 1):
        st = strr[:strr.index(" ")] + strr[strr.index(" ") + 1:]
    else:
        st = strr[:strr.index(" ")]
    return sum([1 for i in range(len(st) - 1) for j in range(i + 1, len(st)) if st[i] > st[j]])


import sys
argv = sys.argv
puzz = argv[1]
from collections import deque
import time
from collections import defaultdict
from heapq import heappop, heappush

#puzz = input("")
check = ""
if '_' in puzz:
    puzz = puzz[0:puzz.index('_')] + " " + puzz[puzz.index('_') + 1:]
arr = list(puzz)
arr = sorted(arr)
for x in range(1, len(arr)):
    check = check + arr[x]
check = check + arr[0]

l = check
h = []
boo2 = False
boo3 = True
retar = []
start = time.time()
seen = set()
# check solvablility
if inv(check) & 1 == 0:
    rowdiff = (abs((check.index(" ") // 4) - (puzz.index(" ") // 4)) & 1)
    puzzin = (inv(puzz) & 1)
    if rowdiff == puzzin:
        boo2 = True
else:
    rowdiff = (abs((check.index(" ") // 4) - (puzz.index(" ") // 4)) & 1)
    puzzin = (inv(puzz) & 1)
    if not rowdiff == puzzin:
        boo2 = True
# check if already solved
if (puzz == check):
    print("Already solved")
    t = time.time() - start
elif (not (boo2)):
    print("Unsolvable")
    t = time.time() - start

else:
    seenmov = create(puzz, check)
    #print(seenmov)
    t = time.time() - start
    o = check
    retar.append(o)
    while (not (seenmov[o] == "")):
        print(seenmov[o])
        retar.append(seenmov[o])
        o = seenmov[o]
    retar = retar[::-1]
    for g in retar:
        p(g)
    print(str((len(retar)) - 1) + " step(s)")
print(str(t))