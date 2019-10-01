from itertools import product
from random import shuffle, sample
import cProfile

def main():
    count = 1
    while True:
        if count%10000 == 0: print(count)
        d = newdeck()
        shuffle(d)
        mn = ([], (9,))
        for h in map(list, (zip(*(d[x:] for x in range(5))))):
            v = value(h)
            if v < mn[1]: mn = h, v
        if mn[1][0] != 0:
            print(count)
            display(d)
            display(mn[0])
            break
        count += 1

def value(cards):
    scards = sorted(cards, key=lambda c: c[0], reverse=True)
    groups = [[] for _ in range(5)]
    prev = scards[0]
    curcount = 1
    straight = scards[0][0] if scards[0][0] >= 4 else False
    flush = scards[0][1] + 1
    for n, s in scards[1:]:
        if n == prev[0]:
	    curcount += 1
        else:
            groups[curcount].append(prev[0])
            curcount = 1
        if straight and n != (prev[0] - 1) % 13:
            straight = False
        if flush and s + 1 != flush:
            flush = False
        prev = (n, s)
    groups[curcount].append(prev[0])

    if groups[1] == [12, 3, 2, 1, 0]:
        straight = 3
    if flush and straight:
        return (8, straight)
    if groups[4]:
        return (7, groups[4][0], groups[1][0])
    if groups[3] and groups[2]:
        return (6, groups[3][0], groups[2][0])
    if flush:
        return (5, *groups[1])
    if straight:
        return (4, straight)
    if groups[3]:
        return (3, groups[3][0], *groups[1])
    if groups[2]:
        return (len(groups[2]), *groups[2], *groups[1])
    return (0, *groups[1])

def hand(deck=None, size=5):
    if not deck:
        deck = newdeck()
        return sample(deck, 5)
    hand = deck[-5:]
    del deck[-5:]
    return hand

def newdeck():
    return list(product(range(13), range(4)))

def display(cards):
    print(' '.join('23456789TJQKA'[n]+'♠♥♣♦'[s] for n,s in cards).replace('T', '10'))

if __name__ == "__main__": main()
