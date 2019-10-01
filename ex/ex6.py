import sys
a, b, c = tuple([int(s) for s in sys.argv[1:]])
p = 0.5 * (a + b + c)
print((p*(p - a)*(p - b)*(p - c))**(0.5))
