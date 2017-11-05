import sys
fib = [1,1]
while len(fib) < int(sys.argv[1]): fib.append(fib[-1]+fib[-2])
print(fib[:int(sys.argv[1])])
