import sys, time
import sudoku as su

filename = 'puzzles.txt' if len(sys.argv) == 1 else sys.argv[1]
puzzles = [line.strip() for line in open(filename)]
template = {}
start = time.time()
for p in puzzles:
    if len(p) not in template: template[len(p)] = su.template(len(p))
    t = template[len(p)]
    print(t.string(p))
    s = su.solver(p, t)
    p = s.solution()
    print(t.string(p))
print("Elapsed time: ", time.time()-start)