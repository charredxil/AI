import sudoku_ec as sudoku
import sys, time
def sudokus_from_file(filename, blanks='0. '):
    sus = []
    with open(filename) as fi:
        for line in fi:
            sus.append(sudoku.makesudoku(line.strip(), blanks))
    return sus

filename = 'puzzles.txt' if len(sys.argv) == 1 else sys.argv[1]
sus = [line.strip() for line in open(filename)]
start = time.time()
for ix, su in enumerate(sus):
    print(ix)
    print(su)
    solved = sudoku.exactcover(su)
    print(solved)
print(str((time.time()-start)))
