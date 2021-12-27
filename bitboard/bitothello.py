"""Python de Othello"""

import copy
from collections import deque
import random

from .bitboard import BitBoard


class OthelloGame:
    """Play othello."""
    BLACK = BitBoard().BLACK
    WHITE = BitBoard().WHITE

    def __init__(self, player_color="black"):
        # Set a board
        self.board = BitBoard()

        # Logger
        self._log_undo = deque([[BitBoard.INIT_WHITE, BitBoard.INIT_BLACK]])
        self._log_redo = deque([])

        # Black or white
        if player_color == "black":
            self._player_color = OthelloGame.BLACK
        if player_color == "white":
            self._player_color = OthelloGame.WHITE
        if player_color == "random":
            self._player_color = random.choice([0, 1])

        # State of game
        self.game_turn = 1
        self.reversible = 0
        self.result = ""

        # Counter
        # [player, opponent, pass] = self._count
        self._disk_count = [2, 2]
        self._pass_count = 0

        # Mode
        self._player_auto = False
        return

    def update_count(self):
        count_board = self.board.count_disks()
        player_cpu = [
            count_board[self._player_color],
            count_board[self._player_color ^ 1],
        ]
        self._disk_count = player_cpu
        return player_cpu

    def auto_mode(self, automode: bool):
        """If True is selected, the match will be played between the CPUs."""
        self._player_auto = automode

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

    def play_turn(self, put_loc: int):
        """You can put disk and reverse opponent's.

        Parameters
        ----------
        put_loc : int
            Integer from 0 to 63.
        """
        put_loc = pow(2, put_loc)
        if self.board.is_reversible(self.game_turn, put_loc):
            board = self.board.simulate_play(self.game_turn, put_loc)
            self.board.play_turn(*board)
            self.game_turn ^= 1
            self._pass_count = 0
            if self._player_color == self.game_turn:
                self._log_undo.append(board)
        return

    def judge_game(self, disk_count: list = None):
        """Judgement of game."""
        if disk_count is None:
            disk_count = self._disk_count

        if self._pass_count >= 2 or sum(disk_count) == 64:
            if disk_count[0] == disk_count[1]:
                self.result = "DRAW"
            if disk_count[0] > disk_count[1]:
                self.result = "WIN"
            if disk_count[0] < disk_count[1]:
                self.result = "LOSE"
            return True
        return False

    def process_game(self):
        if self.judge_game():
            return True

        self.update_count()

        if self.game_turn == self._player_color:
            self.reversible = self.board.reversible_area(self.game_turn)
            if self.board.turn_playable(self.game_turn):
                if self._player_auto:
                    self.play_turn(self._strategy_player.selecter(self))
                else:
                    pass
            else:
                self.game_turn ^= 1
                self._pass_count += 1
        else:
            self.reversible = self.board.reversible_area(self.game_turn)
            if self.board.turn_playable(self.game_turn):
                self.play_turn(self._strategy_opponent.selecter(self))
            else:
                self.game_turn ^= 1
                self._pass_count += 1
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

    def undo_turn(self):
        print("before")
        print(self._log_undo, self._log_redo)
        if not self._log_undo:
            return
        previous_board = self._log_undo.pop()
        self._log_redo.append(previous_board)
        self.board.load_board(*previous_board)
        print("after")
        print(self._log_undo, self._log_redo)
        return

    def redo_turn(self):
        print("before")
        print(self._log_undo, self._log_redo)
        if not self._log_redo:
            return
        next_board = self._log_redo.pop()
        self._log_undo.append(next_board)
        self.board.load_board(*next_board)
        print("after")
        print(self._log_undo, self._log_redo)
        return

    def return_state(self):
        white_board, black_board = self.board.return_board()
        return white_board, black_board, self._log_undo, self._log_redo

    def load_state(self, white_board, black_board, log_undo, log_redo):
        white_board, black_board = self.board.return_board()
        self.board.load_board(white_board, black_board)
        self._log_undo = copy.deepcopy(log_undo)
        self._log_redo = copy.deepcopy(log_redo)
