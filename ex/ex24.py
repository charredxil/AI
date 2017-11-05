import sys, re
print((lambda words: re.sub(words[0], words[1], ' '.join(words[2:])))(sys.argv[1].split()))