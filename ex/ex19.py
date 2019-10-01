import sys, re
print("NOT ONLY DIGITS" if re.search('\D', sys.argv[1]) else "ONLY DIGITS")
