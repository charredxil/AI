import sys, re
print("NOT BINARY" if re.search('[^01]', sys.argv[1]) else int(sys.argv[1], 2))
