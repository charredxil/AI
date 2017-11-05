import sudoku, sys, time
def sudokus_from_file(filename, blanks='0. '):
    sus = []
    with open(filename) as fi:
        for line in fi:
            sus.append(sudoku.makesudoku(line.strip(), blanks))
            if sus[-1] is None: sus.pop()
    return sus

sus = sudokus_from_file('puzzlesHard.txt')
start = time.time()
print(sus[-2])
print(sudoku.exactcover(sus[-2], findall=False))
print(str((time.time()-start)/len(sus)))