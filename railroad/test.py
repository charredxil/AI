from railroad import *
from tkinter import *
import time
import sys

def total(rr, lines=None):
    if not lines: lines = rr.cost
    tot = 0
    for pth in lines:
        tot += rr.cost[pth if pth in rr.cost else (pth[1], pth[0])]
    return tot
def drawastar(rr, rawin):
    #FIX to account for refactoring
    s, e = rr.interpret_input(rawin)
    tkdata = citycanvas(rr)
    path = lines(rr.mapastar(s, e, *tkdata))
    printpath(rr, path, rounddist=4, cols=3)
    highlight(path, *tkdata)
    print("Route Dist:", total(rr, path))
def drawastar(cv, rawin):
    path = lines(cv.astar(*rawin))
    cv.highlight(path)
    printpath(cv.city, path, rounddist=4)
def printpath(rr, path, rounddist=-1, cols=1):
    totdist = 0
    for line in path:
        a = line[0] if line[0] not in rr.node_name else rr.node_name[line[0]]
        b = line[1] if line[1] not in rr.node_name else rr.node_name[line[1]]
        dist = rr.getcost(*line)
        totdist += dist
        print("{} ---> {} ({} km)".format(a, b, str(totdist)[:rounddist]))
    print("Total Distance: {} km".format(totdist))

start = time.time()
am = ('anodes.txt', 'aedges.txt', 'anames.txt')
rom = ('rnodes.txt', 'redges.txt', 'rnames.txt')
rr = citymap(*am)
cities = rr.interpret_input(sys.argv[1:])
for x in rr.adjs['9100620']:
    print(x, rr.getcost('9100620', x))
path = rr.astar(*cities)
printpath(rr, lines(path))
#pathr = list(reversed(rr.astar(cities[1], cities[0])))

"""for ix in range(max(len(path), len(pathr))):
    if ix < len(path): print(path[ix], end='  ')
    else: print("\t", end='')
    if ix < len(pathr): print(pathr[ix])
    else: print()"""

#print("Total Dist:", total(rr), "km")
#cv = citymap_canvas(rr)
#drawastar(cv, cities)
print("Elapsed Time:", time.time()-start, "sec")
#cv.finalize()

