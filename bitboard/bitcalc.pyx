# distutils: language=c++
# cython: language_level=3, boundscheck=False, wraparound=False
# cython: cdivision=True

"""cythonize -3 -a -i .\bitboard\bitcalc.pyx"""


cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cpdef uint64_t bit_count_c(uint64_t x):
    """Count the number of bit awaking.

    Parameters
    ----------
    x : uint64_t
        64-bit intager which represents the location of disk.
    """

    # Distributing by 2-bit, express the number of bits using 2-bit.
    x -= (x >> 1) & 0x5555555555555555ULL
    # Upper 2-bit + lower 2-bit.
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL)
    # Upper 4-bit + lower 4-bit.
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0fULL
    # Upper 8-bit + lower 8-bit.
    x += x >> 8
    # Upper 16-bit + lower 16-bit.
    x += x >> 16
    # Upper 32-bit + lower 32-bit.
    x += x >> 32
    return x & 0x0000007fULL

cpdef uint64_t check_surround_c(uint64_t put_loc, uint64_t direction):
    """Check neighbor disk is reversible or not.

    Parameters
    ----------
    put_loc : uint64_t
        64-bit intager which represents the location of disk.
    direction : uint64_t
        Intager from 0 to 7.
    """
    if direction == 0:  # Upper
        return (put_loc << 8) & 0xffffffffffffff00ULL
    elif direction == 1:  # Upper right
        return (put_loc << 7) & 0x7f7f7f7f7f7f7f00ULL
    elif direction == 2:  # Right
        return (put_loc >> 1) & 0x7f7f7f7f7f7f7f7fULL
    elif direction == 3:  # Lower right
        return (put_loc >> 9) & 0x007f7f7f7f7f7f7fULL
    elif direction == 4:  # Lower
        return (put_loc >> 8) & 0x00ffffffffffffffULL
    elif direction == 5:  # Lower left
        return (put_loc >> 7) & 0x00fefefefefefefeULL
    elif direction == 6:  # Left
        return (put_loc << 1) & 0xfefefefefefefefeULL
    elif direction == 7:  # Upper left
        return (put_loc << 9) & 0xfefefefefefefe00ULL


cpdef uint64_t reversible_area_c(uint64_t turn, uint64_t black_board, uint64_t white_board):
    """Returns reversible area.

    Parameters
    ----------
    turn : uint64_t
        If black is on turn, 1. If white, 0.
    black_board, white_board : uint64_t
        If board is not synchronized with the instance, enter it manually.

    Returns
    -------
    reversible : uint64_t
        Represents board of reversible positions.
    """
    cdef uint64_t *CONST = [
        0x7e7e7e7e7e7e7e7eULL, 0x00ffffffffffff00ULL, 0x007e7e7e7e7e7e00ULL,
    ]
    board = [black_board, white_board]
    blank_board = ~(board[0] | board[1])

    horiz_brd = board[turn ^ 1] & CONST[0]
    vert_brd = board[turn ^ 1] & CONST[1]
    all_border = board[turn ^ 1] & CONST[2]

    # Upper
    one_rv = horiz_brd & (board[turn] << 1)
    one_rv |= horiz_brd & (one_rv << 1)
    one_rv |= horiz_brd & (one_rv << 1)
    one_rv |= horiz_brd & (one_rv << 1)
    one_rv |= horiz_brd & (one_rv << 1)
    one_rv |= horiz_brd & (one_rv << 1)
    reversible = blank_board & (one_rv << 1)

    # Lower
    one_rv = horiz_brd & (board[turn] >> 1)
    one_rv |= horiz_brd & (one_rv >> 1)
    one_rv |= horiz_brd & (one_rv >> 1)
    one_rv |= horiz_brd & (one_rv >> 1)
    one_rv |= horiz_brd & (one_rv >> 1)
    one_rv |= horiz_brd & (one_rv >> 1)
    reversible |= blank_board & (one_rv >> 1)

    # Left
    one_rv = vert_brd & (board[turn] << 8)
    one_rv |= vert_brd & (one_rv << 8)
    one_rv |= vert_brd & (one_rv << 8)
    one_rv |= vert_brd & (one_rv << 8)
    one_rv |= vert_brd & (one_rv << 8)
    one_rv |= vert_brd & (one_rv << 8)
    reversible |= blank_board & (one_rv << 8)

    # Right
    one_rv = vert_brd & (board[turn] >> 8)
    one_rv |= vert_brd & (one_rv >> 8)
    one_rv |= vert_brd & (one_rv >> 8)
    one_rv |= vert_brd & (one_rv >> 8)
    one_rv |= vert_brd & (one_rv >> 8)
    one_rv |= vert_brd & (one_rv >> 8)
    reversible |= blank_board & (one_rv >> 8)

    # Upper right
    one_rv = all_border & (board[turn] << 7)
    one_rv |= all_border & (one_rv << 7)
    one_rv |= all_border & (one_rv << 7)
    one_rv |= all_border & (one_rv << 7)
    one_rv |= all_border & (one_rv << 7)
    one_rv |= all_border & (one_rv << 7)
    reversible |= blank_board & (one_rv << 7)

    # Upper left
    one_rv = all_border & (board[turn] << 9)
    one_rv |= all_border & (one_rv << 9)
    one_rv |= all_border & (one_rv << 9)
    one_rv |= all_border & (one_rv << 9)
    one_rv |= all_border & (one_rv << 9)
    one_rv |= all_border & (one_rv << 9)
    reversible |= blank_board & (one_rv << 9)

    # Lower right
    one_rv = all_border & (board[turn] >> 9)
    one_rv |= all_border & (one_rv >> 9)
    one_rv |= all_border & (one_rv >> 9)
    one_rv |= all_border & (one_rv >> 9)
    one_rv |= all_border & (one_rv >> 9)
    one_rv |= all_border & (one_rv >> 9)
    reversible |= blank_board & (one_rv >> 9)

    # Lower left
    one_rv = all_border & (board[turn] >> 7)
    one_rv |= all_border & (one_rv >> 7)
    one_rv |= all_border & (one_rv >> 7)
    one_rv |= all_border & (one_rv >> 7)
    one_rv |= all_border & (one_rv >> 7)
    one_rv |= all_border & (one_rv >> 7)
    reversible |= blank_board & (one_rv >> 7)
    return reversible
