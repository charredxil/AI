import sys
print(set([p[1] for p in filter(lambda x: x[0] == max([(sys.argv[1].count(char), char) for char in sys.argv[1]])[0], [(sys.argv[1].count(char), char) for char in sys.argv[1]])]))
