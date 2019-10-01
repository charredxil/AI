import sys
dct = {'a' : 0, 'e' : 0, 'i' : 0, 'o' : 0, 'u' : 0}
for char in sys.argv[1]:
    if char in dct.keys(): dct[char] += 1
print(dct) 
