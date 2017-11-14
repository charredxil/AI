from sudoku_hyper import *
import sys, time
def sudokus_from_file(filename, blanks='0. '):
    sus = []
    with open(filename) as fi:
        for line in fi:
            sus.append(sudoku(line.strip()))
    return sus

filename = 'puzzles.txt' if len(sys.argv) == 1 else sys.argv[1]
sus = sudokus_from_file(filename)
#start = time.time()
"""su = sudoku("48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....")
print(su)
su.prune()
print(su)
su.search()
print(su)"""
for num, su in enumerate(sus[54:], start=54):
    print(num)
    print(su)
    #su.prune()
    #print(su)
    su.search()
    print(su)
#print(str((time.time()-start)))