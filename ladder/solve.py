import sys, cProfile, time
from wordgraph import graph
def run():
    start = time.time()
    g = graph('words6.txt')
    wordi, wordf = sys.argv[1], sys.argv[2]
    start = time.time()
    print(g.path(wordi, wordf))
    print("Runtime: {}".format(time.time()-start))
    start = time.time()
    print(g.path2(wordi, wordf))
    print("Runtime: {}".format(time.time()-start))
run()