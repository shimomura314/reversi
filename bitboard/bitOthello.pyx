# distutils: language=c++
# cython: language_level=3, boundscheck=False, wraparound=False
# cython: cdivision=True

"""cythonize -3 -a -i .\bitboard\bitothello.pyx"""

import copy
from collections import deque
from logging import getLogger
import random

from .bitcalc import BitBoardC as BitBoard
# from .bitcalc_ cimport BitBoardC as BitBoard

logger = getLogger(__name__)


cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cdef public class OthelloGameC [object OthelloGameCObject, type OthelloGameCType]:

    # Class variables.
    cdef public int BLACK
    cdef public int WHITE
    cdef public object board
    cdef int _player_clr
    cdef public int turn
    cdef public uint64_t reversible
    cdef public str result
    cdef int _count_player
    cdef int _count_opponent
    cdef int _pass_cnt[2]
    cdef bint _player_auto
    cdef object _strategy_player
    cdef object _strategy_opponent
    cdef object _board_log
    cdef object _board_back

    # Declaration of methods.
    cpdef void play_turn(self, int put_loc)
    cpdef (int, int) update_count(self)
    cpdef bint judge_game(self, int player = 0, int opponent = 0)
    cpdef void auto_mode(self, bint automode = True)
    cpdef void load_strategy(self, object Strategy)
    cpdef void change_strategy(self, str strategy, bint is_player=False)
    cpdef (bint, bint) process_game(self)
    cpdef list display_board(self)
    cpdef bint undo_turn(self)
    cpdef bint redo_turn(self)
    cpdef int return_turn(self)
    # cpdef (uint64_t, uint64_t, list, list) return_state(self)
    cpdef void load_state(
        self, uint64_t black_board, uint64_t white_board,
        list board_log, list board_back)

    def __init__(self, str player_clr="black"):
        # Set a board.
        BLACK = BitBoard().BLACK
        WHITE = BitBoard().WHITE

        self.board = BitBoard()

        # Black or white.
        if player_clr == "black":
            self._player_clr = BitBoard().BLACK
        elif player_clr == "white":
            self._player_clr = BitBoard().WHITE
        elif player_clr == "random":
            self._player_clr = random.choice([0, 1])
        else:
            raise KeyError

        # States of game.
        self.turn = 0
        self.reversible = 0
        self.result = "start"

        # Counter.
        self._count_player = 2
        self._count_opponent = 2
        self._pass_cnt = [0, 0]  # [white, black]

        # Mode.
        self._player_auto = False
        logger.info("Game starts.")

        # Logger.
        self._board_log = deque([])
        self._board_back = deque([])

    cpdef void play_turn(self, int put_loc):
        """You can put disk and reverse opponent's disk.

        Parameters
        ----------
        put_loc : int
            Integer from 0 to 63.
        """
        if not (0 <= put_loc <= 63):
            raise AssertionError
        # cdef uint64_t put_loc_ = 1i64 << put_loc
        cdef uint64_t put_loc_ = pow(2, put_loc)
        cdef uint64_t next_black_board, next_white_board

        # put_loc_ = 1 << put_loc

        # If input value is not valid, raise an error.
        if not self.board.is_reversible(self.turn, put_loc_):
            raise ValueError

        next_black_board, next_white_board = self.board.simulate_play(
            self.turn, put_loc_, 0, 0)

        if self._player_clr == self.turn:
            # Delete roll back log which is no longer used.
            if self._board_back:
                self._board_back = deque([])
            self._board_log.append([next_black_board, next_white_board])

        # Update boards.
        self.board.update_board(next_black_board, next_white_board)
        self._pass_cnt[self.turn] = 0
        self.turn ^= 1

    cpdef (int, int) update_count(self):
        """Update counts of disks."""
        cdef int count_board[2]
        count_board = self.board.count_disks()
        if self._player_clr == 0:
            self._count_player = count_board[0]
            self._count_opponent = count_board[1]
            return count_board[0], count_board[1]
        else:
            self._count_player = count_board[1]
            self._count_opponent = count_board[0]
            return count_board[1], count_board[0]

    cpdef bint judge_game(self, int player = 0, int opponent = 0):
        """Judgement of game."""
        if player == 0 and opponent == 0:
            player = self._count_player
            opponent = self._count_opponent

        # if self._pass_cnt >= 2 or sum(disk_count) == 64:
        cdef uint64_t black, white
        black = self.board.reversible_area(0)
        white = self.board.reversible_area(1)
        if (black == 0 and white == 0) or (player+opponent) == 64:
            if player == opponent:
                self.result = "DRAW"
            if player > opponent:
                self.result = "WIN"
            if player < opponent:
                self.result = "LOSE"
            return True
        return False

    cpdef void auto_mode(self, bint automode = True):
        """If True is selected, the match will be played between the CPUs."""
        self._player_auto = automode

    cpdef void load_strategy(self, object Strategy):
        """Set strategy class."""
        self._strategy_player = Strategy(self)
        self._strategy_opponent = Strategy(self)

    cpdef void change_strategy(self, str strategy, bint is_player=False):
        """You can select AI strategy from candidates below.

        Parameters
        ----------
        strategy : str
            random : Put disk randomly.
            maximize : Put disk to maximize number of one's disks.
            minimize : Put disk to minimize number of one's disks.
        is_player : bool
            Default is False.
        """
        if is_player:
            self._strategy_player.set_strategy(strategy)
        else:
            self._strategy_opponent.set_strategy(strategy)

    cpdef (bint, bint) process_game(self):
        """
        Returns
        -------
        finished, updated : bool
        """
        self.update_count()

        if self.judge_game():
            logger.debug("Game was judged as the end.")
            return True, True

        if self.turn == self._player_clr:
            self.reversible = self.board.reversible_area(self.turn)
            if self.board.turn_playable(self.turn):
                if self._player_auto:
                    logger.debug("Player's turn was processed automatically.")
                    self.play_turn(self._strategy_player.selecter(self))
                    return False, True
                else:
                    pass
            else:
                logger.debug("Player's turn was passed.")
                self.turn ^= 1
                self._pass_cnt[self.turn] += 1
        else:
            self.reversible = self.board.reversible_area(self.turn)
            if self.board.turn_playable(self.turn):
                logger.debug("CPU's turn was processed automatically.")
                self.play_turn(self._strategy_opponent.selecter(self))
                return False, True
            else:
                logger.debug("CPU's turn was passed.")
                self.turn ^= 1
                self._pass_cnt[self.turn] += 1
        return False, False

    cpdef list display_board(self):
        """Calculate 2-dimensional arrays to be used for board display."""
        cdef uint64_t black_board, white_board
        cdef int board_list[8][8]


        black_board, white_board = self.board.return_board()
        board_list = [[0 for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for column in range(8):
                if black_board & 1:
                    board_list[row][column] = 1
                if white_board & 1:
                    board_list[row][column] = -1
                black_board = black_board >> 1
                white_board = white_board >> 1
        return board_list

    cpdef bint undo_turn(self):
        logger.debug(
            "Log:%s - %s" % (
                ", ".join(map(str, self._board_log)),
                ", ".join(map(str, self._board_back)),
                ))
        if not self._board_log:
            logger.warning("The board can not be playbacked.")
            return False

        logger.info("The board was playbacked.")
        previous_board = self._board_log.pop()
        self._board_back.append(self.board.return_board())
        self.board.load_board(*previous_board)

        logger.debug(
            "Log:%s - %s" % (
                ", ".join(map(str, self._board_log)),
                ", ".join(map(str, self._board_back)),
                ))
        return True

    cpdef bint redo_turn(self):
        logger.debug(
            "Log:%s - %s" % (
                ", ".join(map(str, self._board_log)),
                ", ".join(map(str, self._board_back)),
                ))
        if not self._board_back:
            logger.warning("The board can not be advanced.")
            return False
        logger.info("The board was advanced.")
        next_board = self._board_back.pop()
        self._board_log.append(self.board.return_board())
        self.board.load_board(*next_board)
        logger.debug(
            "Log:%s - %s" % (
                ", ".join(map(str, self._board_log)),
                ", ".join(map(str, self._board_back)),
                ))
        return True

    cpdef int return_turn(self):
        return self._player_clr

    # cpdef (uint64_t, uint64_t, list, list) return_state(self):
    #     black_board, white_board = self.board.return_board()
    #     return black_board, white_board, self._board_log, self._board_back

    cpdef void load_state(
            self, uint64_t black_board, uint64_t white_board,
            list board_log, list board_back):
        self.board.load_board(black_board, white_board)
        self._board_log = copy.deepcopy(board_log)
        self._board_back = copy.deepcopy(board_back)
