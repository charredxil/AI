import sys
print(max((sys.argv[1].count(char), char) for char in sys.argv[1])[1])
