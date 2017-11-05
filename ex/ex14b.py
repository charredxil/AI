import sys
print(list(filter(lambda x: sum([x.count(v) for v in 'aeiou']) >= 3, [w for s in sys.argv[1:] for w in s.split()])))
