from collections import deque
def exactcovers(row, col, solution=[], findall=True):
    if not col:
        return [solution.copy()]
    c = min(col, key=lambda c: len(col[c]))
    all_sols = []
    for r in list(col[c]):
        solution.append(r)
        removed_cols = select(row, col, r)
        all_sols.extend(exactcovers(row, col, solution, findall=findall))
        if not findall and len(all_sols) >= 1:
            return all_sols
        deselect(row, col, r, removed_cols) 
        solution.pop()
    return all_sols
def select(row, col, r):
    removed_cols = []
    for satisfied_c in row[r]:
        for useless_r in col[satisfied_c]:
            for c in row[useless_r]:
                if c != satisfied_c: col[c].remove(useless_r)
        removed_cols.append(col.pop(satisfied_c))
    return removed_cols
def deselect(row, col, r, removed_cols):
    for unsatisfied_c in reversed(row[r]):
        col[unsatisfied_c] = removed_cols.pop()
        for useful_r in col[unsatisfied_c]:
            for c in row[useful_r]:
                col[c].add(useful_r)


