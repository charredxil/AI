import cProfile
import time

class Holder:
    def __init__(self, val):
        self.val = val
        self.data_s = None
    def data(self):
        cur = None
        if self.data_s: cur = self.data_s
        else: cur = self
        while isinstance(cur.val, Holder):
            cur = cur.val
        self.data_s = cur
        return cur
def arrange_holders(hrs, ks, pntdct, comps):
    h = None
    if len(hrs) == 1: h = next(iter(hrs))
    else:
        newh = Holder(0)
        comps.add(newh)
        for h in hrs:
            newh.val += h.val
            h.val = newh
            comps.remove(h)
        h = newh
    h.val += 1
    for k in ks:
        pntdct[k] = h
def add_word(word, pntdct, comps):
    hrs = set()
    ks = []
    for ix in range(6):
        k = word[:ix]+'_'+word[ix+1:]
        ks.append(k)
        if k in pntdct:
            hrs.add(pntdct[k].data())
    arrange_holders(hrs, ks, pntdct, comps)
def run():
    start = time.time()
    pntdct = {}
    comps = set()
    with open("words6.txt") as fin:
            for line in fin:
                add_word(line.strip(), pntdct, comps)
    large_comp =  max(comps, key=lambda x: x.val)
    end = time.time()
    print("Number of components:\t{}".format(len(comps)))
    print("Largest component:\t{}".format(large_comp.val))
    print("Time elapsed:\t\t{}".format(end-start))
run()