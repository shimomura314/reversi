"""Python de Othello
"""

from collections import deque
import copy
import numpy as np
from collections import Counter
import random


# print(bin(18411139144890810879))
# print(hex(0b1111111110000001100000011000000110000001100000011000000111111111))

def show(black_board, white_board):
    board_list = [[0 for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for column in range(8):
            if black_board & 1:
                board_list[row][column] = 1
            if white_board & 1:
                board_list[row][column] = -1
            black_board = black_board >> 1
            white_board = white_board >> 1
    for i in range(8):
        print(board_list[i])
    print()
    return board_list

# show(69123178496,34359738387)
# show(69123178496,34359738389)
# show(69123178496,34359738405)

def search_candidates(reversible:int):
    candidates = []
    num = 0
    while reversible:
        if reversible&1:
            candidates.append(num)
        num += 1
        reversible = reversible >> 1
    return candidates

def f(x):
    x = x - ((x >> 1) & 0x5555555555555555)
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0F
    x = (x * 0x0101010101010101) >> 56
    return x

def g(x):
    x -= (x>>1) & 0x5555555555555555
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    x += x >> 8
    x += x >> 16
    x += x >> 32
    return  x & 0x0000007f

for i in range(64):
    x = 2**i
    if f(x) != g(x):
        print(x, f(x), g(x))