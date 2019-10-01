import sys, re
print(re.sub(r'[^\w]|_| ', '', sys.argv[1]))
