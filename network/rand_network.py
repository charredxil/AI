import random
import numpy as np
import matplotlib.pyplot as plt

N = int(10e5)
AVG_DEG = 5

edges = (N*AVG_DEG)/2

nodes = [*range(N)]
net = [set() for _ in range(N)]
deg = [0 for _ in range(N)]
list = nodes.copy()
while edges > 0:
    i = random.randint(0, N-1)
    j = random.choice(list)
    if i in net[j] or i == j: continue
    net[i].add(j); net[j].add(i)
    deg[i] += 1; deg[j] += 1
    list.append(i); list.append(j)
    edges -= 1

deg_count = {}
for d in deg:
    if d not in deg_count:
        deg_count[d] = 0
    deg_count[d] += 1

degs = tuple(sorted(deg_count.keys()))
y_pos = np.arange(len(degs))
count = []
for d in degs:
    count.append(deg_count[d])

plt.bar(y_pos, count, align='center', alpha=0.5)
plt.xticks(y_pos, degs)
plt.ylabel('Count')
plt.xlabel('Degree')
plt.title('Random Network Degree Count (Average Degree = {})'.format(AVG_DEG))
plt.show()
