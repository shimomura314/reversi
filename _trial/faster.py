"""Python de Othello
"""

from collections import deque
import copy
import numpy as np
from collections import Counter
import random
import timeit

EVALUATION1 = np.array([
    30, -12,  0, -1, -1,  0,-12, 30,
    -12,-15, -3, -3, -3, -3,-15,-12,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -12,-15, -3, -3, -3, -3,-15,-12,
    30, -12,  0, -1, -1,  0,-12, 30,
])
EVALUATION2 = [
    30, -12,  0, -1, -1,  0,-12, 30,
    -12,-15, -3, -3, -3, -3,-15,-12,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -12,-15, -3, -3, -3, -3,-15,-12,
    30, -12,  0, -1, -1,  0,-12, 30,
]
EVALUATION3 = (
    30, -12,  0, -1, -1,  0,-12, 30,
    -12,-15, -3, -3, -3, -3,-15,-12,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    -1,  -3, -1, -1, -1, -1, -3, -1,
    0,   -3,  0, -1, -1,  0, -3,  0,
    -12,-15, -3, -3, -3, -3,-15,-12,
    30, -12,  0, -1, -1,  0,-12, 30,
)

exponentiation2 = [pow(2, num) for num in range(64)]
# reversible = 2**64-1

def f1(flag):
    x, y = 123, 456
    return [x, y][0], [x, y][1]

def f2(flag):
    x, y = 123, 456
    if flag:
        return x, y
    else:
        return y, x


number_ = 1000000
x = timeit.timeit(lambda:f1(1), number=number_)
y = timeit.timeit(lambda:f2(1), number=number_)
print(x,y)
# z = timeit.repeat(lambda:print(x/y), repeat=10)
# print(z)
# print(timeit.timeit(lambda:f3(x), number=number_))