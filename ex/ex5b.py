import sys
for num in range(int(sys.argv[1]), int(sys.argv[2])):
    if not sum([1 for x in range(2, num) if num % x == 0]): print(num, end=" ")
