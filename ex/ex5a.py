import sys
num = int(sys.argv[1])
print("NOT PRIME" if sum([1 for x in range(2, num) if num % x == 0]) else "PRIME")
