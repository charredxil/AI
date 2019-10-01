import sys, cProfile
from nqueens import *
qb = queenboard(int(sys.argv[1]))
cProfile.run('qb.solve()')
print(qb)