from slider import *
import cProfile, sys, time
def puz(i=None, g=None):
    a, b = randompzl(4, goal=g, solvable=True)
    if not g: g = b
    if not i: i = a
    past = astar(i, g, manhattan)
    if not past: print("IMPOSSIBLE")
    else: 
        for b in past: 
            if past.count(b) > 1: print(b)
        pstring(past, cols=15, moves=True, pr=True)
def distr(i=None):
    a, _ = randompzl(3)
    if not i: i = a
    d = distribution(i, getboards=True)
    for x in d:
        print("{} : {}".format(x, len(d[x])))
    print(d[max(d.keys())])

start = time.time()
#distr(i=sys.argv[1])
puz(i=sys.argv[1])
print("Time: "+str(time.time()-start))