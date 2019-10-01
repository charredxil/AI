import sys, itertools, cProfile
sys.path.append('A:/')
import general.slow_constraintsat

def no_conflicts(a, b): 
    return a[1] != b[1] and abs(b[0]-a[0]) != abs(a[1]-b[1])
def s(n, vd):
    out = ''
    template = '.'*n+'\n'
    for row in range(n):
        rowstr = template
        if len(vd[row]) == 1:
            col = next(iter(vd[row]))[1]
            rowstr = rowstr[:col] + 'Q' + rowstr[col+1:]
        out += rowstr
    return out
n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
prob = general.slow_constraintsat.problem()
for r in range(n):
    prob.var(r, ((r, c) for c in range(n)))
for x, y in itertools.combinations(range(n), r=2):
    prob.constraint(no_conflicts, (x, y))
prob.one_solution()
print(s(n, prob.var_domain))

