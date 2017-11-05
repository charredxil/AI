import sys
print("ANAGRAMS" if sorted(list(sys.argv[1])) == sorted(list(sys.argv[2])) else "NOT ANAGRAMS")