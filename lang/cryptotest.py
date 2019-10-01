import sys
from random import shuffle
from crypto import decrypt

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def main():
    message = ' '.join(sys.argv[1])
    code = randencode(message)
    print(code)
    decrypt(code)

def randencode(message):
    message = message.upper()
    cipher = list(ALPHABET)
    shuffle(cipher)
    encode = {c : cipher[e] for e, c in enumerate(ALPHABET)}
    code = ''
    for c in message:
        if c not in ALPHABET: code += c
        else: code += encode[c]
    return code

if __name__ == "__main__": main()
