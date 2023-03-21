# distutils: language=c++
# cython: language_level=3, boundscheck=False, wraparound=False
# cython: cdivision=True

"""cythonize -3 -a -i .\bitboard\bitcalc.pyx"""


cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cdef public class BitBoardC [object BitBoardCObject, type BitBoardCType]:

    # Class variables.
    cdef public int BLACK
    cdef public int WHITE
    cdef public uint64_t INIT_BLACK
    cdef public uint64_t INIT_WHITE

    # Instance variables.
    cdef public uint64_t _black_board
    cdef public uint64_t _white_board

    # Declaration of methods.
    cpdef uint64_t _bit_count(self, uint64_t x)
    cpdef uint64_t _check_surround(self, uint64_t put_loc, uint64_t direction)
    cpdef (uint64_t, uint64_t) simulate_play(
        self, int turn, uint64_t put_loc,
        uint64_t black_board = 0, uint64_t white_board = 0,
        )
    cpdef void update_board(self, uint64_t black_board, uint64_t white_board)
    cpdef (uint64_t, uint64_t) count_disks(
            self, uint64_t black_board = 0, uint64_t white_board = 0)
    cpdef uint64_t reversible_area(
        self, uint64_t turn, uint64_t black_board = 0, uint64_t white_board = 0)
    cpdef bint is_reversible(
        self, uint64_t turn, uint64_t put_loc,
        uint64_t black_board = 0, uint64_t white_board = 0,
        )
    cpdef bint turn_playable(
        self, uint64_t turn, uint64_t black_board = 0, uint64_t white_board = 0)
    cpdef (uint64_t, uint64_t) return_board(self)
    cpdef (uint64_t, uint64_t) return_player_board(self, int turn)
    cpdef load_board(self, uint64_t black_board, uint64_t white_board)

    def __cinit__(self):
        self.BLACK = 0
        self.WHITE = 1
        self.INIT_BLACK = 0x0000000810000000ULL
        self.INIT_WHITE = 0x0000001008000000ULL

    def __init__(self):
        self._black_board = 0x0000000810000000ULL
        self._white_board = 0x0000001008000000ULL

    # Difinitions of methods.
    cpdef uint64_t _bit_count(self, uint64_t x):
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

    cpdef uint64_t _check_surround(self, uint64_t put_loc, uint64_t direction):
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

    cpdef (uint64_t, uint64_t) simulate_play(
            self, int turn, uint64_t put_loc,
            uint64_t black_board = 0, uint64_t white_board = 0,
            ):
        """Simulate the next turn.

        Parameters
        ----------
        turn : int
            If black is on turn, 1. If white, 0.
        put_loc : int
            64-bit intager which represents the location of disk.
        black_board, white_board : int
            If board is not synchronized with the instance, enter it manually.

        Returns
        -------
        reversed_black_board, reversed_white_board : list of int
        """
        if black_board  == 0 and white_board == 0:
            black_board = self._black_board
            white_board = self._white_board

        cdef uint64_t reverse_bit = 0
        cdef uint64_t reverse_bit_
        cdef uint64_t border_bit
        if turn == 0:
            # Player is black_board.
            for direction in range(8):
                reverse_bit_ = 0
                border_bit = <uint64_t> self._check_surround(put_loc, direction)
                while border_bit & white_board:
                    reverse_bit_ |= border_bit
                    border_bit = self._check_surround(border_bit, direction)
                # If player's disk is opposite side.
                if border_bit & black_board:
                    reverse_bit |= reverse_bit_
            black_board ^= (put_loc | reverse_bit)
            white_board ^= reverse_bit
        else:
            # Player is white_board.
            for direction in range(8):
                reverse_bit_ = 0
                border_bit = <uint64_t> self._check_surround(put_loc, direction)
                while border_bit & black_board:
                    reverse_bit_ |= border_bit
                    border_bit = self._check_surround(border_bit, direction)
                # If player's disk is opposite side.
                if border_bit & white_board:
                    reverse_bit |= reverse_bit_
            white_board ^= (put_loc | reverse_bit)
            black_board ^= reverse_bit

        return black_board, white_board

    cpdef void update_board(self, uint64_t black_board, uint64_t white_board):
        """Put a disk and reverse opponent disks.

        Parameters
        ----------
        black_board, white_board : int
            64-bit intager.
        """
        self._black_board = black_board
        self._white_board = white_board

    cpdef (uint64_t, uint64_t) count_disks(
            self, uint64_t black_board = 0, uint64_t white_board = 0):
        """Returns black and white's disk number.

        Parameters
        ----------
        black_board, white_board : int (optional)
            64-bit intager.
        """
        if black_board  == 0 and white_board == 0:
            black_board = self._black_board
            white_board = self._white_board

        return self._bit_count(black_board), self._bit_count(white_board)

    cpdef uint64_t reversible_area(
            self, uint64_t turn, uint64_t black_board = 0, uint64_t white_board = 0):
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
        if black_board  == 0 and white_board == 0:
            black_board = self._black_board
            white_board = self._white_board

        cdef uint64_t *CONST = [
            0x7e7e7e7e7e7e7e7eULL, 0x00ffffffffffff00ULL, 0x007e7e7e7e7e7e00ULL,
        ]
        cdef uint64_t *board = [black_board, white_board]
        cdef uint64_t blank_board = ~(board[0] | board[1])

        cdef uint64_t horiz_brd = board[turn ^ 1] & CONST[0]
        cdef uint64_t vert_brd = board[turn ^ 1] & CONST[1]
        cdef uint64_t all_border = board[turn ^ 1] & CONST[2]

        # Upper
        cdef uint64_t one_rv = horiz_brd & (board[turn] << 1)
        one_rv |= horiz_brd & (one_rv << 1)
        one_rv |= horiz_brd & (one_rv << 1)
        one_rv |= horiz_brd & (one_rv << 1)
        one_rv |= horiz_brd & (one_rv << 1)
        one_rv |= horiz_brd & (one_rv << 1)
        cdef uint64_t reversible = blank_board & (one_rv << 1)

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

    cpdef bint is_reversible(
            self, uint64_t turn, uint64_t put_loc,
            uint64_t black_board = 0, uint64_t white_board = 0,
            ):
        """Return wheather you can put disk on (x,y) or not.

        Parameters
        ----------
        turn : int
            If black is on turn, 1. If white, 0.
        put_loc : int
            64-bit intager which represents the location of disk.
        black_board, white_board : int (optional)
            64-bit intager.

        Returns
        -------
        is_reversible : bool
        """
        if black_board  == 0 and white_board == 0:
            black_board = self._black_board
            white_board = self._white_board

        reversible = self.reversible_area(turn, black_board, white_board)
        return (put_loc & reversible) == put_loc

    cpdef bint turn_playable(
            self, uint64_t turn, uint64_t black_board = 0, uint64_t white_board = 0):
        """Return wheather you can put disk or not.

        Parameters
        ----------
        turn : int
            If black is on turn, 1. If white, 0.
        put_loc : int
            64-bit intager which represents the location of disk.
        black_board, white_board : int (optional)
            64-bit intager.
        """
        if black_board  == 0 and white_board == 0:
            black_board = self._black_board
            white_board = self._white_board

        reversible = self.reversible_area(turn, black_board, white_board)
        return reversible != 0

    cpdef (uint64_t, uint64_t) return_board(self):
        return self._black_board, self._white_board

    cpdef (uint64_t, uint64_t) return_player_board(self, int turn):
        if turn == 0:
            return self._black_board, self._white_board
        else:
            return self._white_board, self._black_board

    cpdef load_board(self, uint64_t black_board, uint64_t white_board):
        self._black_board = black_board
        self._white_board = white_board
