import sys, time, cProfile
from wordgraph import graph
def allmax(objs, key=lambda x: x):
    maxval = None
    maxes = None
    for obj in objs:
        val = key(obj)
        if not maxval or val > maxval:
            maxval = val
            maxes = {obj,}
        elif val == maxval:
            maxes.add(obj)
    return maxes
def data():
    start = time.time()
    g = graph('words6.txt', adjs=True, comps=True)
    print("Graph construction time: {}".format(time.time()-start))
    print("Edges: {}".format(g.edges))
    print("Vertices: {}".format(g.vertices))
    print("Components: {}".format(len(g.comps)))
    gcomp = max(g.comps, key=len)
    print("Greatest component size: {}".format(len(gcomp)))
    #print("Greatest component: {}".format(gcomp))
    if len(sys.argv) > 1:
        word = sys.argv[1]
        print("Neighbors to '{}': {}".format(word, g.adjacents(word)))
    mostadjs = allmax(g.adjs, key=lambda w: len(g.adjs[w]))
    mostex = next(iter(mostadjs))
    numadjs = len(g.adjs[mostex])
    if len(mostadjs) == 1:
        print("'{}' has the most neighbors, with {}".format(mostex, numadjs))
    else:
        print("{} each have the most neighbors, with {}".format(mostadjs, numadjs))
    print("Total runtime: {}".format(time.time()-start))
data()