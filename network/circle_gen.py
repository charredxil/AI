import random
import math

cases = []
TRAINS = 10000
TESTS = 100000
EPS = 0.05
OVER, UNDER = 1, 0
'''for t in range(TRAINS):
    dist = -2
    while dist < 0: dist = random.gauss(1, 1)
    a = random.uniform(-dist, dist)
    b = math.sqrt(dist**2 - a**2)
    if random.random() < 0.5: b *= -1
    s = OVER if (a**2 + b**2) > 1 else UNDER
    cases.append(" ".join([str(a), str(b), "=>", str(s)]))'''

for _ in range(TRAINS+TESTS):
    a = random.uniform(-1.5, 1.5)
    b = random.uniform(-1.5, 1.5)
    s = 0.5*math.sqrt(a**2 + b**2)
    cases.append(" ".join([str(a), str(b), "=>", str(s)]))

tr = cases[:TRAINS]
te = cases[TRAINS:]

with open("data/circle.txt", "w") as f:
    print("\n".join(tr), file=f)
    print(file=f)
    print("\n".join(te), file=f)
