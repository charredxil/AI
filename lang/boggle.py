import sys
import re
import itertools
from random import random
from collections import namedtuple

Cube = namedtuple("Cube", "lets x y")

class Node:
    def __init__(self, next=None, full=False, prefix=''):
        self.next = next if next else {}
        self.full = full
        self.prefix = prefix

class Grid:
    def __init__(self, letters, minword=None):
        self.letters = letters
        self.side = int(len(letters)**0.5)
        self.minword = minword if minword else (3 if self.side <= 4 else 4)
        self.cubes = [Cube(ls, e%self.side, e//self.side) for e, ls in enumerate(letters)]
        self.adj = {}
        for cu in self.cubes:
            self.adj[cu] = set()
            for dx, dy in itertools.product([-1, 0, 1], repeat=2):
                if (dx, dy) == (0, 0): continue
                nx, ny = cu.x + dx, cu.y + dy
                if 0 <= ny < self.side and 0 <= nx < self.side:
                    adj_cu = self.cubes[nx + ny*self.side]
                    self.adj[cu].add(adj_cu)
    def __str__(self):
        return '\n'.join(''.join(self.letters[x*self.side:(x+1)*self.side]) for x in range(0, self.side))

def random_grid(side, dict_name = 'enable1'):
    let_cumfreq = [('-', 0)]
    with open('docs/{}_letterfreq.txt'.format(dict_name)) as f:
        for l, fq in map(lambda l: tuple(l.split()), list(f)):
            let_cumfreq.append((l, let_cumfreq[-1][1]+float(fq)))
    letters = ''
    for r in [random() for _ in range(side**2)]:
        for l, cfq in let_cumfreq:
            if r < cfq:
                letters += l
                break
    return Grid(letters)


def find_words(grid, trie):
    words = set()
    for cu in grid.cubes:
        node = trie
        for ch in cu.lets:
            if ch in node.next: node = node.next[ch]
            else: break
        else: _find_words(grid, node, cu, {cu}, words)
    return words
def _find_words(grid, node, cube, used, words):
    if node.full and len(node.prefix) >= grid.minword:
        words.add(node.prefix)
    for cu in grid.adj[cube]:
        if cu in used: continue
        next_node = node
        for ch in cu.lets:
            if ch in next_node.next: next_node = next_node.next[ch]
            else: break
        else:
            used.add(cu)
            _find_words(grid, next_node, cu, used, words)
            used.remove(cu)

def select_words(dict, grid):
    chars = '|'.join(set(grid.letters))
    lookahead = r'(?=.{' + str(grid.minword) + ',})'
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

def interpret_input(s):
    if s.isdigit():
        return random_grid(int(s))
    letters = []
    ix = 0
    while ix < len(s):
        num = 0
        while s[ix].isdigit():
            num = num*10 + int(s[ix])
            ix += 1
        if not num: num = 1
        letters.append(s[ix:num+ix].lower())
        ix += num
    return Grid(letters)

def main(inp, dict_name='scrabble', printout=False):
    grid = inp
    if type(inp) == type("abc") or type(inp) == type(1):
        grid = interpret_input(str(inp))

    dict_path = 'docs/' + dict_name + '.txt'
    dict = open(dict_path).read().lower()
    words = select_words(dict, grid)
    trie = create_trie(words)

    words = find_words(grid, trie)
    ordered = sorted(words)
    ordered.sort(key=len, reverse=True)

    if printout:
        print(grid, end='\n\n')
        print(' '.join(ordered))
        print(len(words), 'words')

    return grid, ordered

if __name__ == "__main__":
    main(sys.argv[1], printout=True)
