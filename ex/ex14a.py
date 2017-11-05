import sys
print(list(filter(lambda x: x[0] in 'aeiou' and x[-1] in 'aeiou', [w for s in sys.argv[1:] for w in s.split()])))
