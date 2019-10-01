from collections import namedtuple
import re
import sys

Letter = namedtuple("Letter", "ch L W id")

def show_letter(l):
    o = l.ch
    if l.L != 1:
        o += str(l.L) + 'L'
    if l.W != 1:
        o += str(l.W) + 'W'
    return o

def show_word(w):
    return "".join(l.ch for l in w) + "\n" + " ".join(show_letter(l) for l in w)

def order_letters(word, letters):
    order = []
    used = set()
    for ch in word:
        for l in letters:
            if l in used: continue
            if l.ch == ch:
                used.add(l)
                order.append(l)
                break
    return tuple(order)

value = {'a': 1, 'b': 4, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 3, 'h': 3, 'i': 1,
         'j': 10, 'k': 5, 'l': 2, 'm': 4, 'n': 2, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
         's': 1, 't': 1, 'u': 2, 'v': 6, 'w': 4, 'x': 8, 'y': 4, 'z': 10}
class Node:
    def __init__(self, next=None, full=False, prefix=''):
        self.next = next if next else {}
        self.full = full
        self.prefix = prefix

def simplify(letters):
    return {l.ch for l in letters}

def select_words(dict, letters):
    chars = '|'.join(simplify(letters))
    lookahead = r'(?=.{2,})'
    allow = re.compile('^{}({})*$'.format(lookahead, chars), re.M)
    return map(lambda m: m.group(0), allow.finditer(dict))

def create_trie(words):
    root = Node()
    for word in words:
        cur = root
        for c in word:
            if c not in cur.next:
                cur.next[c] = Node(prefix = cur.prefix+c)
            cur = cur.next[c]
        cur.full = True
    return root

def interpret_input(ss):
    letters = set()
    for id, s in enumerate(ss):
        ch = s[0].lower()
        L, W = 1, 1
        if len(s) > 1 and s[-1].upper() == 'L': L = int(s[1:-1])
        if len(s) > 1 and s[-1].upper() == 'W': W = int(s[1:-1])
        letters.add(Letter(ch, L, W, id))
    return letters

def calculate_score(letters):
    score = sum(value[l.ch]*l.L for l in letters)
    for l in letters: score *= l.W
    return score

def all_words(letters, trie):
    words = set()
    for start in letters:
        node = trie
        if start.ch in node.next:
            node = node.next[start.ch]
            _all_words(letters, node, {start}, words)
    return words
def _all_words(letters, node, used, words):
    if node.full:
        words.add(order_letters(node.prefix, used.copy()))
    for l in letters - used:
        if l.ch in node.next:
            next_node = node.next[l.ch]
            used.add(l)
            _all_words(letters, next_node, used, words)
            used.remove(l)
    return words

def best_word(letters, trie):
    best = (0, "", set())
    for start in letters:
        node = trie
        if start.ch in node.next:
            node = node.next[start.ch]
            best = _best_word(letters, node, {start}, best)
    return order_letters(best[1], best[2])
def _best_word(letters, node, used, best):
    if node.full:
        score = calculate_score(used)
        if score > best[0]: best = (score, node.prefix, used.copy())
    for l in letters - used:
        if l.ch in node.next:
            next_node = node.next[l.ch]
            used.add(l)
            best = _best_word(letters, next_node, used, best)
            used.remove(l)
    return best

def best_pair(letters, trie):
    allws = all_words(letters, trie)
    best = 0, None, None
    for w1 in allws:
        w2 = best_word(letters - set(w1), trie)
        score = calculate_score(w1) + calculate_score(w2)
        if score > best[0]:
            best = score, w1, w2
    return best[1:]

letters = interpret_input(sys.argv[1:])
dict_name = "wordss"
dict_path = 'docs/' + dict_name + '.txt'
dict = open(dict_path).read().lower()
words = select_words(dict, letters)
trie = create_trie(words)

w1, w2 = best_pair(letters, trie)
print(show_word(w1))
print(show_word(w2))
