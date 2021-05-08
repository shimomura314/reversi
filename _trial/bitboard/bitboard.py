"""Python de Othello
Citation : https://othelloq.com/programming/bit-board
"""

from collections import deque
import copy
import random


class BitBoard:
    """Play othello.
    Black disk make the first move.
    White disk make the second move.
    """
    BLACK = 1
    WHITE = 0
    INIT_BLACK = 0x0000000810000000
    INIT_WHITE = 0x0000001008000000

    def __init__(self):
        # Set a board
        self._black_board = BitBoard.INIT_BLACK
        self._white_board = BitBoard.INIT_WHITE
        self.game_turn = BitBoard.BLACK

        # Logger
        self._log = deque(())
        self._log.append((self._black_board, self._white_board))
        self._log_redo = deque(())
        return

    def update(self, black_board: int, white_board: int):
        """Update a state of instance."""
        self._black_board = black_board
        self._white_board = white_board
        self._log.append((black_board, white_board))
        self._log_redo = deque(())
        return

    def bit_count(self, x: int):
        """Count the number of bit awaking.
        
        Parameters
        ----------
        x : int
            64-bit intager.
        """
        # Distributing by 2-bit, express the number of bits using 2-bit integer.
        x -= (x>>1) & 0x5555555555555555
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
        return  x & 0x0000007f

    def count_disks(self, black_board: int, white_board: int, player_color: int):
        """Returns player and opponent's disk number.

        Returns
        ----------
        count_player, count_opponent : int
        """
        if player_color:
            return self.bit_count(black_board), self.bit_count(white_board)
        else:
            return self.bit_count(white_board), self.bit_count(black_board)

    def change_turn(self):
        self.game_turn ^= 1
        return

    def reversible_area(self, black_board: int, white_board: int, game_turn: int):
        """Returns reversible area."""
        if game_turn:
            player, opponent = black_board, white_board
        else:
            player, opponent = white_board, black_board
        blank_board = ~(black_board | white_board)

        horizontal_border = opponent & 0x7e7e7e7e7e7e7e7e
        vertical_border   = opponent & 0x00ffffffffffff00
        all_border        = opponent & 0x007e7e7e7e7e7e00

        # Upper
        one_reversible = horizontal_border & (player << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        one_reversible |= horizontal_border & (one_reversible << 1)
        reversible = blank_board & (one_reversible << 1)

        # Lower
        one_reversible = horizontal_border & (player >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        one_reversible |= horizontal_border & (one_reversible >> 1)
        reversible |= blank_board & (one_reversible >> 1)
        
        # Left
        one_reversible = vertical_border & (player << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        one_reversible |= vertical_border & (one_reversible << 8)
        reversible |= blank_board & (one_reversible << 8)

        # Right
        one_reversible = vertical_border & (player >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        one_reversible |= vertical_border & (one_reversible >> 8)
        reversible |= blank_board & (one_reversible >> 8)
        
        # Upper right
        one_reversible = all_border & (player << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        one_reversible |= all_border & (one_reversible << 7)
        reversible |= blank_board & (one_reversible << 7)

        # Upper left
        one_reversible = all_border & (player << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        one_reversible |= all_border & (one_reversible << 9)
        reversible |= blank_board & (one_reversible << 9)

        # Lower right
        one_reversible = all_border & (player >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        one_reversible |= all_border & (one_reversible >> 9)
        reversible |= blank_board & (one_reversible >> 9)

        # Lower left
        one_reversible = all_border & (player >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        one_reversible |= all_border & (one_reversible >> 7)
        reversible |= blank_board & (one_reversible >> 7)
        return reversible

    def is_reversible(self, input_: int, reversible: int):
        """Return wheather you can put disk on (x,y) or not.
        
        Parameters
        ----------
        input_ : int
            64-bit intager.
        """
        return (input_ & reversible) == input_

    def check_surroundings(self, input_: int, direction: int):
        """Check neighbor disk is reversible or not.
        
        Used parameters
        ---------------
        0xffffffffffffff00
        0x7f7f7f7f7f7f7f00
        0x7f7f7f7f7f7f7f7f
        0x007f7f7f7f7f7f7f
        0x00ffffffffffffff
        0x00fefefefefefefe
        0xfefefefefefefefe
        0xfefefefefefefe00

        0b       0b       0b       0b      
        11111111 01111111 01111111 00000000
        11111111 01111111 01111111 01111111
        11111111 01111111 01111111 01111111
        11111111 01111111 01111111 01111111
        11111111 01111111 01111111 01111111
        11111111 01111111 01111111 01111111
        11111111 01111111 01111111 01111111
        00000000 00000000 01111111 01111111

        0b       0b       0b       0b 
        00000000 00000000 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 11111110
        11111111 11111110 11111110 00000000

        Parameters
        ----------
        input_ : int
            64-bit intager.
        """
        if direction == 0: # Upper
            return (input_ << 8) & 0xffffffffffffff00
        elif direction == 1: # Upper right
            return (input_ << 7) & 0x7f7f7f7f7f7f7f00
        elif direction == 2: # Right
            return (input_ >> 1) & 0x7f7f7f7f7f7f7f7f
        elif direction == 3: # Lower right
            return (input_ >> 9) & 0x007f7f7f7f7f7f7f
        elif direction == 4: # Lower
            return (input_ >> 8) & 0x00ffffffffffffff
        elif direction == 5: # Lower left
            return (input_ >> 7) & 0x00fefefefefefefe
        elif direction == 6: # Left
            return (input_ << 1) & 0xfefefefefefefefe
        elif direction == 7: # Upper left
            return (input_ << 9) & 0xfefefefefefefe00
        else:
            return 0

    def reverse(self, black_board: int, white_board: int, game_turn: int, input_: int):
        """Put a disk and reverse disks.

        Parameters
        ----------
        input_ : int
            64-bit intager.

        Returns
        ----------
        black_board, white_board : int
        """
        if game_turn:
            player, opponent = black_board, white_board
        else:
            player, opponent = white_board, black_board
        blank_board = ~(black_board | white_board)

        reverse_bit = 0
        for direction in range(8):
            reverse_bit_ = 0
            border_bit = self.check_surroundings(input_, direction)
            while (border_bit != 0) and ((border_bit & opponent) != 0):
                reverse_bit_ |= border_bit
                border_bit = self.check_surroundings(border_bit, direction)
            if (border_bit & player) != 0:
                reverse_bit |= reverse_bit_
        player ^= (input_ | reverse_bit)
        opponent ^= reverse_bit
        if game_turn:
            return player, opponent
        else:
            return opponent, player

    def turn_playable(self, reversible: int):
        """Return wheather you can put disk or not."""
        return reversible != 0

    def log_turn(self):
        """Append data to board_log."""
        return self._log.append((self._black_board, self._white_board))

    def undo_turn(self):
        if self._log != deque(()):
            self._log_redo.append(self._log.pop())
            self._black_board, self._white_board = self._log[-1]
        return

    def redo_turn(self):
        if self._log_redo != deque(()):
            self._log.append(self._log_redo.pop())
            self._black_board, self._white_board = self._log[-1]
        return