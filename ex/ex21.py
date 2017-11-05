import sys, re
print("NOT HEX" if re.search('[^0-9A-Fa-f]', sys.argv[1]) else int(sys.argv[1], 16))
