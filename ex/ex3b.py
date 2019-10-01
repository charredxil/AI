import sys
print([int(s) for s in sys.argv[1:] if int(s) % 3 == 0])
