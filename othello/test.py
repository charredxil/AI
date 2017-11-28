from board import *
b, w = initial()
a = allmoves(b, w)
display({'X': b, 'O': w, '+': a})
