# distutils: language=c++
# cython: language_level=3, boundscheck=False, wraparound=False
# cython: cdivision=True

"""cythonize -3 -a -i .\strategy\minmaxcalc.pyx"""

import cython
from cython.view cimport array


cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cdef extern from "math.h":
    float INFINITY


cdef public class MinmaxC [object MinmaxCObject, type MinmaxCType]:

    cdef int _EVAL_TBL1[64]
    cdef int _EVAL_TBL2[64]
    cdef uint64_t _EXP2[64]
    cdef int _player_clr
    cdef int _count_pass
    cdef object _othello

    def __cinit__(self):
        self._EVAL_TBL1[0:64] = [
            30,  -12,   0,  -1,  -1,   0, -12,  30,
            -12, -15,  -3,  -3,  -3,  -3, -15, -12,
            0,    -3,   0,  -1,  -1,   0,  -3,   0,
            -1,   -3,  -1,  -1,  -1,  -1,  -3,  -1,
            -1,   -3,  -1,  -1,  -1,  -1,  -3,  -1,
            0,    -3,   0,  -1,  -1,   0,  -3,   0,
            -12, -15,  -3,  -3,  -3,  -3, -15, -12,
            30,  -12,   0,  -1,  -1,   0, -12,  30,
        ]
        self._EVAL_TBL2[0:64] = [
            120, -20,  20,   5,   5,  20, -20, 120,
            -20, -40,  -5,  -5,  -5,  -5, -40, -20,
            20,   -5,  15,   3,   3,  15,  -5,  20,
            5,    -5,   3,   3,   3,   3,  -5,   5,
            5,    -5,   3,   3,   3,   3,  -5,   5,
            20,   -5,  15,   3,   3,  15,  -5,  20,
            -20, -40,  -5,  -5,  -5,  -5, -40, -20,
            120, -20,  20,   5,   5,  20, -20, 120,
        ]
        self._EXP2[0:64] = [
            1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192,
            16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152,
            4194304, 8388608, 16777216, 33554432, 67108864, 134217728,
            268435456, 536870912, 1073741824, 2147483648, 4294967296,
            8589934592, 17179869184, 34359738368, 68719476736, 137438953472,
            274877906944, 549755813888, 1099511627776, 2199023255552,
            4398046511104, 8796093022208, 17592186044416, 35184372088832,
            70368744177664, 140737488355328, 281474976710656, 562949953421312,
            1125899906842624, 2251799813685248, 4503599627370496,
            9007199254740992, 18014398509481984, 36028797018963968,
            72057594037927936, 144115188075855872, 288230376151711744,
            576460752303423488, 1152921504606846976, 2305843009213693952,
            4611686018427387904, 9223372036854775808,
        ]

    cdef int touch_border(self, uint64_t black_board, uint64_t white_board)
    cdef float evaluate_value(self, uint64_t black_board, uint64_t white_board)
    cdef (float, int) min_max(
        self, uint64_t black_board, uint64_t white_board, int turn,
        int depth, float pre_evaluation
        )
    cpdef int put_disk(self, object othello, int depth=4)

    cdef int touch_border(self, uint64_t black_board, uint64_t white_board):
        cdef uint64_t board = (black_board | white_board)
        if board & 0xff818181818181ffULL:
            return 1
        return 0

    cdef float evaluate_value(self, uint64_t black_board, uint64_t white_board):
        cdef float evaluation = 0
        cdef uint64_t *board = [black_board, white_board]

        # If disk does not touch the border,
        # phase is False and TABLE[0] is called.
        phase = self.touch_border(black_board, white_board)
        for position in range(64):
            if phase == 0:
                # If a disc is on an edge square.
                if (self._EXP2[position] & board[self._player_clr]):
                    evaluation += self._EVAL_TBL1[position]
                if (self._EXP2[position] & board[self._player_clr ^ 1]):
                    evaluation -= self._EVAL_TBL1[position]
            else:
                if (self._EXP2[position] & board[self._player_clr]):
                    evaluation += self._EVAL_TBL2[position]
                if (self._EXP2[position] & board[self._player_clr ^ 1]):
                    evaluation -= self._EVAL_TBL2[position]
        return evaluation

    cdef (float, int) min_max(
            self, uint64_t black_board, uint64_t white_board, int turn,
            int depth, float pre_evaluation
            ):
        """Return wheather you can put disk or not.

        Parameters
        ----------
        black_board, white_board : int (optional)
            64-bit intager.
        turn : int
            If black is on turn, 1. If white, 0.
        """
        # Calculate evaluation.
        cdef float evaluation = self.evaluate_value(black_board, white_board)
        cdef float max_evaluation
        cdef float min_evaluation
        cdef float next_evaluation 
        cdef uint64_t new_black_board
        cdef uint64_t new_white_board
        cdef int count_black
        cdef int count_white
        cdef int selected
        cdef int candidate

        if depth == 0:
            return evaluation, 1

        if turn == self._player_clr:
            max_evaluation = -1 * INFINITY
        else:
            min_evaluation = INFINITY

        cdef uint64_t reversible = self._othello.board.reversible_area(
            turn, black_board, white_board
            )

        cdef list candidates = []
        for num in range(64):
            if self._EXP2[num] & reversible:
                candidates.append(num)

        if self._othello.board.turn_playable(
            turn, black_board, white_board
        ):
            for candidate in candidates:
                new_black_board, new_white_board = \
                    self._othello.board.simulate_play(
                        turn, self._EXP2[candidate],
                        black_board, white_board,
                    )
                count_black, count_white = self._othello.board.count_disks(
                    new_black_board, new_white_board
                )
                if self._player_clr:
                    count_player, count_opponent = count_black, count_white
                else:
                    count_player, count_opponent = count_white, count_black
                if self._othello.judge_game([count_player, count_opponent]):
                    if self._othello.result == "WIN":
                        next_evaluation = 10000000000
                    elif self._othello.result == "LOSE":
                        next_evaluation = -10000000000
                    else:
                        next_evaluation = 0
                else:
                    if turn == self._player_clr:
                        next_evaluation = self.min_max(
                            new_black_board, new_white_board,
                            turn ^ 1, depth-1, max_evaluation,
                            )[0]
                    else:
                        next_evaluation = self.min_max(
                            new_black_board, new_white_board,
                            turn ^ 1, depth-1, min_evaluation,
                            )[0]

                # alpha-bata method(pruning)
                if turn == self._player_clr:
                    if next_evaluation > pre_evaluation:
                        return pre_evaluation, candidate
                else:
                    if pre_evaluation > next_evaluation:
                        return pre_evaluation, candidate

                if turn == self._player_clr:
                    if max_evaluation < next_evaluation:
                        max_evaluation = next_evaluation
                        selected = candidate
                else:
                    if next_evaluation < min_evaluation:
                        min_evaluation = next_evaluation
                        selected = candidate
        else:
            if turn == self._player_clr:
                return self.min_max(
                    black_board, white_board, turn^1, depth-1, max_evaluation,
                    )
            else:
                return self.min_max(
                    black_board, white_board, turn^1, depth-1, min_evaluation,
                    )
        if turn == self._player_clr:
            return max_evaluation, selected
        else:
            return min_evaluation, selected

    cpdef int put_disk(self, object othello, int depth=4):
        cdef uint64_t new_black_board
        cdef uint64_t new_white_board

        black_board, white_board = othello.board.return_board()
        cdef int turn = othello.turn
        self._player_clr = turn
        self._count_pass = 0
        self._othello = othello
        return self.min_max(
            black_board, white_board, turn, depth, INFINITY)[1]
