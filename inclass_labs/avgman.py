from argparse import Namespace
import math, time, sys, random, cProfile
def getdata(goal):
    data = {}
    cols = int(math.sqrt(len(goal)))
    data['cols'] = cols
    data['lu'] = {ix : set() for ix in range(len(goal))}
    for ix in range(len(goal)):
        if ix % cols != cols-1: data['lu'][ix].add((1, -1, ix+1))
        if ix % cols != 0: data['lu'][ix].add((1, 1, ix-1))
        if ix + cols < cols**2: data['lu'][ix].add((0, -1, ix+cols))
        if ix - cols >= 0: data['lu'][ix].add((0, 1, ix-cols))
    return Namespace(**data)
start = time.time()
board, _ix = list('ABCDEFGHIJKLMNO '), 15
diff = {ch : [0, 0] for ch in board if ch != ' '}
data = getdata(board)
manhattan = manhattan_sum = 0
n = int(sys.argv[1])
for _ in range(n):
    rc, d, _new = random.sample(data.lu[_ix], 1)[0]
    board[_ix], board[_new] = board[_new], board[_ix]
    manhattan += 1 if d*diff[board[_ix]][rc] >= 0 else -1
    diff[board[_ix]][rc] += d
    _ix = _new
    manhattan_sum += manhattan
elapsedtime = time.time()-start
print("N = {} boards analyzed".format(n))
print("TIME = {} sec".format(elapsedtime))
print("AVG MANHATTAN DIST = {} moves".format(manhattan_sum/n))
print("N/TIME = {} boards analyzed per sec".format(n/elapsedtime))
# N = 3000000 boards analyzed
# TIME = 13.584463834762573 sec
# AVG MANHATTAN DIST = 37.01849933333333 moves
# N/TIME = 220840.5157900318 boards analyzed per sec
