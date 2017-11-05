import sys
from nqueens import *
qb = queenboard(int(sys.argv[1]))
qb.solve()
print(qb)