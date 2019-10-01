import sys
if len(sys.argv) == 2:
    num = int(sys.argv[1])
    print("NOT PRIME" if sum([1 for x in range(2, num) if num % x == 0]) else "PRIME")
else:
    for num in range(int(sys.argv[1]), int(sys.argv[2])):
        if not sum([1 for x in range(2, num) if num % x == 0]): print(num, end=" ")
