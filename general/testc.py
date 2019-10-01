import constraintsat as c
p = c.problem()
p.var("a", [2, 3])
p.var("b", [1, 2, 3])
p.constraint(lambda a, b: a != b, ("a", "b"))
p.one_solution()
print(p.var_domain)