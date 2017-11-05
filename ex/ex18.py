import sys
print(''.join([sys.argv[1][x] for x in range(len(sys.argv[1])) if sys.argv[1][x] not in sys.argv[1][:x]]))
