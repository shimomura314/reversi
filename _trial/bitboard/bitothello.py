"""Python de Othello
"""

import random

from .bitboard import BitBoard

class OthelloGame:
    """Play othello.
    Black disk make the first move.
    White disk make the second move.
    """
    BLACK = 1
    WHITE = 0
    BOARD_SIZE = 8

    def __init__(self, player_color='black'):
        # Set a board
        self.board = BitBoard()

        # Black or white
        if player_color == "black":
            self._player_color = OthelloGame.BLACK
        if player_color == "white":
            self._player_color = OthelloGame.WHITE
        if player_color == "random":
            self._player_color = random.choice([0, 1])

        # Counter
        self.result = ""
        self.count_player = 2
        self.count_opponent = 2
        self.count_blank = 60
        self.count_pass = 0
        self.reversible = 0

        # Mode
        self.player_auto = False
        return

    def auto_mode(self, automode: bool):
        self.player_auto = automode

    def load_strategy(self, Strategy):
        """Set strategy class."""
        self._Strategy_player = Strategy(self)
        self._Strategy_player.set_strategy("random")
        self._Strategy_opponent = Strategy(self)
        self._Strategy_opponent.set_strategy("random")

    def put_disk(self, input_: int):
        """You can put disk and reverse opponent's.

        Parameters
        ----------
        input_ : int
            Integer from 0 to 63.
        """
        input_ = pow(2, input_)
        reversible = self.board.reversible_area(self.board._black_board, self.board._white_board, self.board.game_turn)
        if self.board.is_reversible(input_, reversible):
            black_board, white_board = self.board.reverse(self.board._black_board, self.board._white_board, self.board.game_turn, input_)
            self.board.update(black_board, white_board)
            self.board.change_turn()
            self.count_pass = 0
        return

    def change_strategy(self, strategy, is_player=False):
        """You can select AI strategy from candidates below.

        Parameters
        ----------
        strategy : str
            random : Put disk randomly.
            maximize : Put disk to maximize number of one's disks.
            minimize : Put disk to minimize number of one's disks.
            openness : Put disk based on openness theory.
            evenness : Put disk based on evenness theory.

        is_player : bool
            Default is False.
        """
        if is_player:
            self._Strategy_player.set_strategy(strategy)
        else:
            self._Strategy_opponent.set_strategy(strategy)
        return

    def process_game(self):
        if self.game_judgement():
            return True
        count_player, count_opponent = self.board.count_disks(self.board._black_board, self.board._white_board, self._player_color)
        self.count_player = count_player
        self.count_opponent = count_opponent
        self.count_blank = 64 - count_player - count_opponent
        reversible = self.board.reversible_area(self.board._black_board, self.board._white_board, self.board.game_turn)
        self.reversible = reversible

        if self.board.game_turn == self._player_color:
            if self.board.turn_playable(reversible):
                if self.player_auto:
                    self.put_disk(self._Strategy_player.selecter(self))
                else:
                    pass
            else:
                self.board.change_turn()
                self.count_pass += 1
        else:
            if self.board.turn_playable(reversible):
                self.put_disk(self._Strategy_opponent.selecter(self))
            else:
                self.board.change_turn()
                self.count_pass += 1
            self.board.log_turn()
        return False

    def display_board(self):
        """Show the game board."""
        black_board, white_board = self.board._black_board, self.board._white_board
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

    def game_judgement(self):
        """Judgement of game."""
        if self.count_pass >= 2 or self.count_blank == 0:
            if self.count_player == self.count_opponent:
                self.result = "DRAW"
            if self.count_player > self.count_opponent:
                self.result = "WIN"
            if self.count_player < self.count_opponent:
                self.result = "LOSE"
            return True
        return False