class CharNode:
    def __init__(self, ch, kids=[]):
        self.ch = ch
        self.kids = kids
prefixes = lambda word: (word[:x] for x in range(len(word)))
def remove_unreachables(words):
    words.sort(key=len)
    noprefix = set()
    for word in words:
        if sum(1 for pre in prefixes(word) if pre in noprefix) == 0:
            noprefix.add(word)
    return noprefix
def build_tree(words):
    root = CharNode('')
    cur = root
    for word in words:
        makenew = False
        for ch in word:
            found = False
            for kid in cur.kids:
                if kid.ch == ch:
                    cur = kid
                    found = True
                    break
            if not found:
                newnode = CharNode(ch)
                cur.kids.append(newnode)
                break



enable1 = open("enable1.txt")
words = [word.strip() for word in enable1]
words = remove_unreachables(words)