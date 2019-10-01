import sys, re, math

improper_chars = re.compile(r"[^A-Z]")

freq_name = 'freq'
f = None
with open('docs/{}.txt'.format(freq_name)) as f:
    f =  {w.strip().upper() : math.log(int(c)) for w, c in map(lambda l: tuple(l.split()), list(f))}

def frequency(word):
    count = f.get(word)
    return count if count is not None else 0

s = sys.argv[1].upper()
words = [improper_chars.sub('', w) for w in s.split()]
print(words)
ranks = [frequency(w) for w in words]
print(ranks)
print(sum(ranks))
