class unionfind:
    def __init__(self):
        self.weight = {}
        self.parent = {}
    def add(self, obj):
        if obj not in self.parent:
            self.parent[obj] = obj
            self.weight[obj] = 1
    def find(self, obj):
        path = [obj]
        root = self.parent[obj]
        while root != path[-1]:
            path.append(root)
            root = self.parent[root]
        for p in path:
            self.parent[p] = root
        return root
    def union(self, *objs):
        roots = [self.find(x) for x in objs]
        mx = max(roots, key=lambda r: self.weight[r])
        for r in roots:
            if r != mx:
                self.weight[mx] += self.weight[r]
                self.parent[r] = mx
    def getsets(self):
        comp = {}
        for obj in self.parent:
            root = self.find(obj)
            if root in comp:
                comp[root].add(obj)
            else:
                comp[root] = {obj,}
        return list(comp.values())