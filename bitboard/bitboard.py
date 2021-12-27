"""
This file defines the system of Reversi.
Black disk make the first move, and white disk make the second move.
"""

# from functools import lru_cache


class BitBoard:

    __all__ = [
        "simulate_play", "play_turn",
        "count_disks", "reversible_area", "is_reversible", "turn_playable",
        "return_board", "return_player_board", "load_board",
        ]

    BLACK = 1
    WHITE = 0
    INIT_BLACK = 0x0000000810000000
    INIT_WHITE = 0x0000001008000000

    def __init__(self):
        # Set a board
        self._white_board = BitBoard.INIT_WHITE
        self._black_board = BitBoard.INIT_BLACK
        return

    @staticmethod
    # @lru_cache()
    def _bit_count(x: int):
        """Count the number of bit awaking.

        Parameters
        ----------
        x : int
            64-bit intager which represents the location of disk.
        """
        # Distributing by 2-bit, express the number of bits using 2-bit.
        x -= (x >> 1) & 0x5555555555555555
        # Upper 2-bit + lower 2-bit.
        x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
        # Upper 4-bit + lower 4-bit.
        x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
        # Upper 8-bit + lower 8-bit.
        x += x >> 8
        # Upper 16-bit + lower 16-bit.
        x += x >> 16
        # Upper 32-bit + lower 32-bit.
        x += x >> 32
        return x & 0x0000007f

    @staticmethod
    # @lru_cache()
    def _check_surroundings(put_loc: int, direction: int):
        """Check neighbor disk is reversible or not.

        Parameters
        ----------
        put_loc : int
            64-bit intager which represents the location of disk.
        direction : int
            Intager from 0 to 7.
        """
        if direction == 0:  # Upper
            return (put_loc << 8) & 0xffffffffffffff00
        if direction == 1:  # Upper right
            return (put_loc << 7) & 0x7f7f7f7f7f7f7f00
        if direction == 2:  # Right
            return (put_loc >> 1) & 0x7f7f7f7f7f7f7f7f
        if direction == 3:  # Lower right
            return (put_loc >> 9) & 0x007f7f7f7f7f7f7f
        if direction == 4:  # Lower
            return (put_loc >> 8) & 0x00ffffffffffffff
        if direction == 5:  # Lower left
            return (put_loc >> 7) & 0x00fefefefefefefe
        if direction == 6:  # Left
            return (put_loc << 1) & 0xfefefefefefefefe
        if direction == 7:  # Upper left
            return (put_loc << 9) & 0xfefefefefefefe00
        return 0

    def simulate_play(
            self, game_turn: int, put_loc: int,
            white_board: int = None, black_board: int = None,
            ):
        """Simulate the next turn.

        Parameters
        ----------
        game_turn : int
            If black is on turn, 1. If white, 0.
        put_loc : int
            64-bit intager which represents the location of disk.
        black_board, white_board : int
            If board is not synchronized with the instance, enter it manually.

        Returns
        ----------
        reversed_black_board, reversed_white_board : int
        """
        if white_board is None:
            white_board = self._white_board
            black_board = self._black_board
        board = [white_board, black_board]

        # Player is board[game_turn].
        reverse_bit = 0
        for direction in range(8):
            reverse_bit_ = 0
            border_bit = self._check_surroundings(put_loc, direction)
            while border_bit & board[game_turn ^ 1]:
                reverse_bit_ |= border_bit
                border_bit = self._check_surroundings(border_bit, direction)
            # If player's disk is opposite side.
            if border_bit & board[game_turn]:
                reverse_bit |= reverse_bit_
        board[game_turn] ^= (put_loc | reverse_bit)
        board[game_turn ^ 1] ^= reverse_bit

        return board

    def play_turn(self, white_board=None, black_board=None):
        """Put a disk and reverse opponent disks.

        Parameters
        ----------
        game_turn : int
            If black, 1. If white, 0.
        put_loc : int
            64-bit intager.
        """
        self._white_board = white_board
        self._black_board = black_board
        return

    def count_disks(self, white_board=None, black_board=None):
        """Returns white and black's disk number."""
        if white_board is None:
            white_board = self._white_board
            black_board = self._black_board
        board = [white_board, black_board]
        return list(map(self._bit_count, board))

    def reversible_area(
            self, game_turn: int,
            white_board: int = None, black_board: int = None,
            ):
        """Returns reversible area."""
        if white_board is None:
            white_board = self._white_board
            black_board = self._black_board
        board = [white_board, black_board]
        blank_board = ~(board[0] | board[1])

        horizontal_border = board[game_turn ^ 1] & 0x7e7e7e7e7e7e7e7e
        vertical_border = board[game_turn ^ 1] & 0x00ffffffffffff00
        all_border = board[game_turn ^ 1] & 0x007e7e7e7e7e7e00

        # Upper
        one_reversible = horizontal_border & (board[game_turn] << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        reversible = blank_board & (one_reversible << 1)

        # Lower
        one_reversible = horizontal_border & (board[game_turn] >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        reversible |= blank_board & (one_reversible >> 1)

        # Left
        one_reversible = vertical_border & (board[game_turn] << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        reversible |= blank_board & (one_reversible << 8)

        # Right
        one_reversible = vertical_border & (board[game_turn] >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        reversible |= blank_board & (one_reversible >> 8)

        # Upper right
        one_reversible = all_border & (board[game_turn] << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        reversible |= blank_board & (one_reversible << 7)

        # Upper left
        one_reversible = all_border & (board[game_turn] << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        reversible |= blank_board & (one_reversible << 9)

        # Lower right
        one_reversible = all_border & (board[game_turn] >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        reversible |= blank_board & (one_reversible >> 9)

        # Lower left
        one_reversible = all_border & (board[game_turn] >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        reversible |= blank_board & (one_reversible >> 7)
        return reversible

    def is_reversible(self, game_turn: int, put_loc: int):
        """Return wheather you can put disk on (x,y) or not.

        Parameters
        ----------
        put_loc : int
            64-bit intager.
        """
        reversible = self.reversible_area(
            game_turn, self._white_board, self._black_board
            )
        return (put_loc & reversible) == put_loc

    def turn_playable(
            self, game_turn: int,
            white_board: int = None,
            black_board: int = None,
            ):
        """Return wheather you can put disk or not."""
        if white_board is None:
            white_board = self._white_board
            black_board = self._black_board
        reversible = self.reversible_area(game_turn, white_board, black_board)
        return reversible != 0

    def return_board(self):
        return self._white_board, self._black_board

    def return_player_board(self, game_turn: int):
        board = [self._white_board, self._black_board]
        return board[game_turn], board[game_turn ^ 1]

    def load_board(self, white_board, black_board):
        self._white_board = white_board
        self._black_board = black_board
