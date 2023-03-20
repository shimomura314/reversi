"""
This file defines the system of Reversi.
Black disk make the first move, and white disk make the second move.
"""

# from functools import lru_cache
from logging import getLogger

from .bitcalc import BitBoardC

logger = getLogger(__name__)


class BitBoard:

    __all__ = [
        "simulate_play", "update_board",
        "count_disks", "reversible_area", "is_reversible", "turn_playable",
        "return_board", "return_player_board", "load_board",
        ]

    BLACK = 0
    WHITE = 1
    INIT_BLACK = 0x0000000810000000
    INIT_WHITE = 0x0000001008000000

    def __init__(self):
        self._black_board = BitBoard.INIT_BLACK
        self._white_board = BitBoard.INIT_WHITE
        self._cboard = BitBoardC()
        logger.info("Board was set.")

    def simulate_play(
            self, turn: int, put_loc: int,
            black_board: int = None, white_board: int = None,
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
        if black_board is None:
            black_board = self._black_board
            white_board = self._white_board
        return self._cboard.simulate_play(
            turn, put_loc, black_board, white_board)

    def update_board(self, black_board, white_board):
        """Put a disk and reverse opponent disks.

        Parameters
        ----------
        black_board, white_board : int
            64-bit intager.
        """
        self._black_board = black_board
        self._white_board = white_board
        self._cboard.update_board(black_board, white_board)

    def count_disks(self, black_board=None, white_board=None):
        """Returns black and white's disk number.

        Parameters
        ----------
        black_board, white_board : int (optional)
            64-bit intager.
        """
        if black_board is None:
            black_board = self._black_board
            white_board = self._white_board
        return self._cboard.count_disks(black_board, white_board)

    def reversible_area(
            self, turn: int, black_board: int = None, white_board: int = None):
        """Returns reversible area.

        Parameters
        ----------
        turn : int
            If black is on turn, 1. If white, 0.
        black_board, white_board : int
            If board is not synchronized with the instance, enter it manually.

        Returns
        -------
        reversible : int
            Represents board of reversible positions.
        """
        if black_board is None:
            black_board = self._black_board
            white_board = self._white_board
        return self._cboard.reversible_area(turn, black_board, white_board)

    def is_reversible(
            self, turn: int, put_loc: int,
            black_board: int = None, white_board: int = None,
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
        if black_board is None:
            black_board = self._black_board
            white_board = self._white_board
        return self._cboard.is_reversible(
            turn, put_loc, black_board, white_board)

    def turn_playable(
            self, turn: int, black_board: int = None, white_board: int = None,
            ):
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
        if black_board is None:
            black_board = self._black_board
            white_board = self._white_board
        reversible = self._cboard.reversible_area(turn, black_board, white_board)
        return reversible != 0

    def return_board(self):
        return self._black_board, self._white_board

    def return_player_board(self, turn: int):
        board = [self._black_board, self._white_board]
        return board[turn], board[turn ^ 1]

    def load_board(self, black_board, white_board):
        self._black_board = black_board
        self._white_board = white_board
        self._cboard.load_board(black_board, white_board)


if __name__ == "__main__":
    from bitcalc import BitBoardC
    BitBoardp = BitBoard()
    BitBoardc = BitBoardC()
    x = 0x0000000810000000
    y = 0x0000001008000000
    # BitBoardc.update_board(4, 2**28-1)
    # BitBoardp.update_board(4, 2**28-1)

    print(BitBoardc.simulate_play(0, 2**26, x, y))
    print(BitBoardp.simulate_play(0, 2**26, x, y))

    print(BitBoardc.count_disks(x, y))
    print(BitBoardp.count_disks(x, y))

    print(BitBoardc.reversible_area(0, x, y))
    print(BitBoardp.reversible_area(0, x, y))

    print(BitBoardc.is_reversible(0, 2**26, x, y))
    print(BitBoardp.is_reversible(0, 2**26, x, y))

    print(BitBoardc.turn_playable(1, x, y))
    print(BitBoardp.turn_playable(1, x, y))

    print(BitBoardc.return_board())
    print(BitBoardp.return_board())

    print(BitBoardc.return_player_board(1))
    print(BitBoardp.return_player_board(1))
