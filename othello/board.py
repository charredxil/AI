from bitarray import bitarray
def initial():
    white = black = 0
    black |= 1 << 27
    black |= 1 << 36
    white |= 1 << 35
    white |= 1 << 28
    return black, white
def allmoves(p, o):
    omask = o & 0x7E7E7E7E7E7E7E7E
    full = 0xFFFFFFFFFFFFFFFF
    moves = somemoves(p, omask, 1)
    moves |= somemoves(p, o, 8)
    moves |= somemoves(p, omask, 7)
    moves |= somemoves(p, omask, 9)
    return moves & (full ^ (p|o))
def makemove(p, o, move):
    return
def somemoves(p, omask, delta):
    flip = ((p << delta) | (p >> delta)) & omask
    for x in range(5):
        flip |= ((flip << delta) | (flip >> delta)) & omask
    return (flip << delta) | (flip >> delta)
def display(char_board):
    for ix in range(64):
        if ix % 8 == 0 and ix != 0: print()
        printed = False
        for ch, board in char_board.items():
            if board & 1: 
                print(ch, end='')
                printed=True
            char_board[ch] >>= 1
        if not printed: print('.', end='')