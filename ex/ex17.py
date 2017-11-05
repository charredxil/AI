import sys
print([sys.argv[1][x] for x in range(len(sys.argv[1])) if (x+1 == len(sys.argv[1]) or sys.argv[1][x] != sys.argv[1][x+1]) and (x == 0 or sys.argv[1][x] != sys.argv[1][x-1])][0])
