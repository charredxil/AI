import math
import random
import sys
import pprint

### Squashing Function ###

def f(x):
    #return 1.1/(1 + math.exp(-x))
    return math.tanh(x)
    #return (0 if x <= 0 else x*x)
def f_at(fx):
    #return 1.1*fx*(1-fx)
    return 1/(math.cosh(fx)**2)
    #return 0 if fx == 0 else 2*(math.sqrt(fx))

### Neural Network Struct ###

class net:
    def __init__(n, *nodes):
        n.layers = len(nodes)
        n.fr = tuple([c+1 if e != n.layers-1 else c for e, c in enumerate(nodes)])
        n.to = nodes
        n.w = [[[random.uniform(-1.5, 1.5) for to in range(n.to[ly+1])] for fr in range(n.fr[ly])] for ly in range(n.layers-1)]
        n.func = f
        n.func_at = f_at
    def array_filled(n, fill):
        return [[[fill for to in range(n.to[ly+1])] for fr in range(n.fr[ly])] for ly in range(n.layers-1)]

### Neural Network Methods ###

def net_run(n, inp):
    x = [inp + (1,)]
    for layer in range(1, n.layers):
        cur = []
        for to in range(n.to[layer]):
            val = sum(n.w[layer-1][fr][to]*x[-1][fr] for fr in range(n.fr[layer-1]))
            cur.append(val)
        if layer != n.layers-1:
            x.append(tuple(map(n.func, cur)) + (1,))
        else:
            x.append(tuple(cur))
    return tuple(x)

def learning_rate(iter):
    s = STEP_INIT*math.exp(STEP_DECAY*iter)
    return s

def net_backprop(n, x, err, iter, delta):
    for layer in range(n.layers-2, -1, -1):
        cur = []
        if layer != 0:
            for fr in range(n.fr[layer]):
                val = sum(n.w[layer][fr][to]*err[to] for to in range(n.to[layer+1]))*n.func_at(x[layer][fr])
                cur.append(val)
        for fr in range(n.fr[layer]):
            for to in range(n.to[layer+1]):
                partial = x[layer][fr]*err[to]
                delta[layer][fr][to] += learning_rate(iter)*partial
        err = cur

def net_update(n, delta, momentum, batch_size):
    for layer in range(0, n.layers-1):
        for fr in range(n.fr[layer]):
            for to in range(n.to[layer+1]):
                delta[layer][fr][to] *= (1/batch_size)
                if momentum is not None:
                    delta[layer][fr][to] += MOMENTUM_RATE*momentum[layer][fr][to]
                n.w[layer][fr][to] += delta[layer][fr][to]

def net_train(n, in_out, runs, batch_size=None):
    if batch_size is None or batch_size > len(in_out):
        batch_size = len(in_out)
    momentum = None
    for r in range(runs):
        delta = n.array_filled(0)
        for i, o in random.sample(in_out, batch_size):
            x = net_run(n, i)
            err = [o[to] - x[-1][to] for to in range(n.to[-1])]
            net_backprop(n, x, err, r, delta)
        net_update(n, delta, momentum, batch_size)
        #if r % 1000 == 0: net_test(n, in_out)
        momentum = delta

### I/O ###

def get_data(fn):
    train = None
    cur = []
    for line in open(fn):
        toks = line.strip().split()
        if len(toks) <= 1:
            train, cur = tuple(cur), []
            continue
        brk = toks.index("=>")
        i = tuple(map(float, toks[:brk]))
        o = tuple(map(float, toks[brk+1:]))
        cur.append((i, o))
    test = tuple(cur)
    train = train if train is not None else test
    return (train, test)

def net_test(n, test):
    tot_err = 0
    correct = 0
    for i, o in test:
        x = net_run(n, i)
        tot_err += sum((o[to] - x[-1][to])**2 for to in range(n.to[-1]))
        if o[0] >= 0.5 and x[-1][0] >= 0.5:
            correct += 1
        elif o[0] <= 0.5 and x[-1][0] <= 0.5:
            correct += 1
        #print("{} => {}".format(form(i), form(x[-1])))
    print("AVG ERROR:", tot_err/(2*len(test)))
    print("RUNS:", RUNS)
    pp = pprint.PrettyPrinter()
    pp.pprint(n.w)
    print("{}/{}".format(correct, len(test)))

form = lambda v: "(" + ", ".join(map(lambda s: "{0:+.15f}".format(s), v)) + ")"

FILE = "circle"
RUNS = 10000
STEP_INIT = 0.2
STEP_FINAL = 0.1
STEP_DECAY= (1/RUNS)*math.log(STEP_FINAL/STEP_INIT)
MOMENTUM_RATE = 0.8
BATCH_SIZE = 50
HIDDEN_STRUCTURE = (6,)
def main():
    file_name = sys.argv[1] if len(sys.argv) > 1 else FILE
    data_file = "data/{}.txt".format(file_name)
    train, test = get_data(data_file)
    in_L, out_L = len(train[0][0]), len(train[0][1])
    n = net(in_L, *HIDDEN_STRUCTURE, out_L)
    net_train(n, train, RUNS, BATCH_SIZE)
    net_test(n, test)

if __name__ == "__main__": main()
