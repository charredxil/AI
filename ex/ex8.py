import sys, re
nopunct = re.sub(r'[^\w]|_| ', '', sys.argv[1]).lower()
print("NOT PALINDROME" if sum([1 for a, b in zip(nopunct, reversed(nopunct)) if a != b]) else "PALINDROME")
