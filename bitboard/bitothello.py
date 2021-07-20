"""Python de Othello"""

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

    def __init__(self, player_color="black"):
        # Set a board
        self.board = BitBoard()

        # Black or white
        if player_color == "black":
            self._player_color = OthelloGame.BLACK
        if player_color == "white":
            self._player_color = OthelloGame.WHITE
        if player_color == "random":
            self._player_color = random.choice([0, 1])

        self.game_turn = 1

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

    def put_disk(self, put_loc: int):
        """You can put disk and reverse opponent's.

        Parameters
        ----------
        put_loc : int
            Integer from 0 to 63.
        """
        put_loc = pow(2, put_loc)
        if self.board.is_reversible(self.game_turn, put_loc):
            self.board.put_disk(self.game_turn, put_loc)
            self.game_turn ^= 1
            self.count_pass = 0
        return

    def load_strategy(self, Strategy):
        """Set strategy class."""
        self._strategy_player = Strategy(self)
        self._strategy_player.set_strategy("random")
        self._strategy_opponent = Strategy(self)
        self._strategy_opponent.set_strategy("random")

    def change_strategy(self, strategy, is_player=False):
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
        return

    def _update_count(self):
        count_board = self.board.count_disks()
        self.count_player, self.count_opponent = (
            count_board[self._player_color],
            count_board[self._player_color ^ 1],
            )
        self.count_blank = 64 - sum(count_board)

    def process_game(self):
        if self.game_judgement():
            return True

        self._update_count()

        if self.game_turn == self._player_color:
            self.reversible = self.board.reversible_area(self.game_turn)
            if self.board.turn_playable(self.game_turn):
                if self.player_auto:
                    self.put_disk(self._strategy_player.selecter(self))
                else:
                    pass
            else:
                self.game_turn ^= 1
                self.count_pass += 1
        else:
            self.reversible = self.board.reversible_area(self.game_turn)
            if self.board.turn_playable(self.game_turn):
                self.put_disk(self._strategy_opponent.selecter(self))
            else:
                self.game_turn ^= 1
                self.count_pass += 1
        return False

    def display_board(self):
        """Show the game board."""
        white_board, black_board = self.board.return_board()
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

    def game_judgement(
        self,
        count_player: int = None,
        count_opponent: int = None,
        count_blank: int = None
    ):
        """Judgement of game."""
        if count_player is None:
            count_player = self.count_player
        if count_opponent is None:
            count_opponent = self.count_opponent
        if count_blank is None:
            count_blank = self.count_blank

        if self.count_pass >= 2 or self.count_blank == 0:
            if self.count_player == self.count_opponent:
                self.result = "DRAW"
            if self.count_player > self.count_opponent:
                self.result = "WIN"
            if self.count_player < self.count_opponent:
                self.result = "LOSE"
            return True
        return False
