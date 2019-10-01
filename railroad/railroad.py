import sys
sys.path.append('A:/')
import useful as u
from math import pi, acos, sin, cos, inf
from heapq import heappop, heappush, heapify
from tkinter import *

class citymap:
    def __init__(self, nodesf, edgesf, namesf):
        self.drawn = False
        self.loc = {}
        self.adjs = {}
        self.cost = {}
        self.node_name = {}
        self.name_node = {}
        with open(nodesf) as f:
            for line in f:
                node, lat, lng = tuple(line.strip().split(sep=' '))
                self.loc[node] = (float(lat), float(lng))
                self.adjs[node] = set()
        with open(edgesf) as f:
            for line in f:
                a, b = tuple(line.strip().split(sep=' '))
                dist = self.globedist(a, b)
                self.adjs[a].add(b)
                self.adjs[b].add(a)
                self.cost[(a, b)] = dist
        with open(namesf) as f:
            for line in f:
                node, *name = tuple(line.strip().split(sep=' '))
                name = ' '.join(name)
                self.node_name[node] = name
                self.name_node[name] = node
    def globedist(self, a, b):
        R = 6371
        conv = pi/180.0
        y1 = self.loc[a][0] * conv
        x1 = self.loc[a][1] * conv
        y2 = self.loc[b][0] * conv
        x2 = self.loc[b][1] * conv
        return acos(sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(x2-x1)) * R
    def interpret_input(self, parts):
        stop = 1
        while ' '.join(parts[:stop]) not in self.name_node:
            stop += 1
            if stop > len(parts): return None
        c1, c2 = " ".join(parts[:stop]), " ".join(parts[stop:])
        return (self.name_node[c1], self.name_node[c2])
    def astar(self, start, end):
        return u.astar(start, end, lambda x: self.adjs[x], self.globedist, cost=self.getcost, data=end)
    def mapastar(self, root, goal, master, canvas, line_id):
        node_id = {}
        prev = {}
        g = {root : 0}
        op = {root : self.globedist(root, goal)}
        q = [(op[root], root)]
        cl = set()
        while q:
            fval, node = heappop(q)
            for succ in self.adjs[node]:
                if succ == goal: return u.path(node, prev) + [goal]
                if succ in cl: continue
                g[succ] = g[node] + self.getcost(node, succ)
                newf = self.globedist(succ, goal) + g[succ]
                if succ not in op or newf < op[succ]:
                    i = line_id[(node, succ) if (node, succ) in line_id else (succ, node)]
                    canvas.itemconfig(i, fill="green")
                    node_id[succ] = i
                    heappush(q, (newf, succ))
                    op[succ] = newf
                    prev[succ] = node
            if node in op: del op[node]
            cl.add(node)
            if node != root: canvas.itemconfig(node_id[node], fill="purple")
            if not len(cl) % 500: master.update()
        master.update()
    def flatcoords(self, width, height, margin):
        coord = {}
        minlng = minlat = 361.0
        maxlng = maxlat = -1
        for node in self.loc:
            loc = self.loc[node]
            lat = loc[0] if loc[0] > 0 else 360 + loc[0]
            lng = loc[1] if loc[1] > 0 else 360 + loc[1]
            if lat < minlat: minlat = lat
            elif lat > maxlat: maxlat = lat
            if lng < minlng: minlng = lng
            elif lng > maxlng: maxlng = lng
            coord[node] = (lat, lng)
        latv = minlat if maxlat - minlat <= 180 else maxlat
        lngv = minlng if maxlng - minlng <= 180 else maxlng
        latr = maxlat - minlat if maxlat - minlat <= 180 else 360 + minlat - maxlat
        lngr = maxlng - minlng if maxlng - minlng <= 180 else 360 + minlng - maxlng
        conv = min(((height - 2*margin)/latr), ((width - 2*margin)/lngr))
        for node in coord:
            pt = coord[node]
            y = ((pt[0] - latv) % 360) * conv + (height - latr*conv)/2
            x = ((pt[1] - lngv) % 360) * conv + (width - lngr*conv)/2
            coord[node] = (x, height-y)
        return coord
    def getcost(self, a, b):
        if (a, b) in self.cost: return self.cost[(a, b)]
        if (b, a) in self.cost: return self.cost[(b, a)]
        return inf
#converts a list of nodes to a list of paths between nodes
def lines(path):
    l = []
    for ix in range(len(path)-1):
        l.append((path[ix], path[ix+1]))
    return l
class citymap_canvas:
    def __init__(self, city):
        self.city = city
        self.master = Tk()
        self.canvas = Canvas(self.master, width=1000, height=600)
        self.line_id = {}
        self.coord = city.flatcoords(1000, 600, 25)
        for path in city.cost:
            col, thck = 'black', 1
            self.line_id[path] = self.canvas.create_line(*self.coord[path[0]], *self.coord[path[1]], fill=col, width=thck)
        self.canvas.pack()
    def highlight(self, tohi):
        for path in tohi:
            path = path if path in self.line_id else (path[1], path[0])
            self.canvas.itemconfig(self.line_id[path], fill='red', width=3)
    def astar(self, root, goal):
        node_id = {}
        prev = {}
        g = {root : 0}
        op = {root : self.city.globedist(root, goal)}
        q = [(op[root], root)]
        cl = set()
        while q:
            fval, node = heappop(q)
            for succ in self.city.adjs[node]:
                if succ == goal: return u.path(node, prev) + [goal]
                if succ in cl: continue
                g[succ] = g[node] + self.city.getcost(node, succ)
                newf = self.city.globedist(succ, goal) + g[succ]
                if succ not in op or newf < op[succ]:
                    i = self.line_id[(node, succ) if (node, succ) in self.line_id else (succ, node)]
                    self.canvas.itemconfig(i, fill="green")
                    node_id[succ] = i
                    heappush(q, (newf, succ))
                    op[succ] = newf
                    prev[succ] = node
            if node in op: del op[node]
            cl.add(node)
            if node != root: self.canvas.itemconfig(node_id[node], fill="purple")
            if not len(cl) % 500: self.master.update()
        master.update()
    def finalize(self):
        mainloop()


