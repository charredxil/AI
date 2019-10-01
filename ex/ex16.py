import sys
print(max(zip(sys.argv[1], sys.argv[1][1:]), key=lambda t: abs(ord(t[0])-ord(t[1]))))
