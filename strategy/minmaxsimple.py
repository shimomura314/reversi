"""Various strategies for othello.
"""

from collections import deque
import copy
import numpy as np
import pickle
import random

from bitboard import OthelloGame

class MinmaxSimple:
    """Find a better move by min-max method.
    """
    __all__ = ["put_disk"]

    def __init__(self, filename='./strategy/minmaxsimple_hash.pkl'):
        self._filename = filename
        try:
            with open(filename, 'rb') as file_:
                self._hash_log = pickle.load(file_)
        except:
            self._hash_log = {}
        for color in ["1", "0"]:
            for turn in ['1', '0']:
                for depth in map(str, range(10)):
                    key = "".join([color, turn, depth])
                    if key not in self._hash_log.keys():
                        self._hash_log[key] = {}

        self._EVALUATION_FIRST = [
            30, -12,  0, -1, -1,  0,-12, 30,
            -12,-15, -3, -3, -3, -3,-15,-12,
            0,   -3,  0, -1, -1,  0, -3,  0,
            -1,  -3, -1, -1, -1, -1, -3, -1,
            -1,  -3, -1, -1, -1, -1, -3, -1,
            0,   -3,  0, -1, -1,  0, -3,  0,
            -12,-15, -3, -3, -3, -3,-15,-12,
            30, -12,  0, -1, -1,  0,-12, 30,
        ]
        self._EVALUATION_MIDDLE = [
            120,-20, 20,  5,  5, 20,-20,120,
            -20,-40, -5, -5, -5, -5,-40,-20,
            20,  -5, 15,  3,  3, 15, -5, 20,
            5,   -5,  3,  3,  3,  3, -5,  5,
            5,   -5,  3,  3,  3,  3, -5,  5,
            20,  -5, 15,  3,  3, 15, -5, 20,
            -20,-40, -5, -5, -5, -5,-40,-20,
            120,-20, 20,  5,  5, 20,-20,120,
        ]

        self._exponentiation2 = [pow(2, num) for num in range(64)]
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
                    pass
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

    def game_judgement(self, count_player:int, count_opponent:int, count_blank:int):
        """Judgement of game."""
        if self._count_pass >= 2 or count_blank == 0:
            if count_player == count_opponent:
                self._result = "DRAW"
            if count_player > count_opponent:
                self._result = "WIN"
            if count_player < count_opponent:
                self._result = "LOSE"
            return True
        return False

    def touch_border(self, black_board, white_board):
        board = (black_board | white_board)
        return (board & 0xff818181818181ff)

    def evaluate_value(self, black_board, white_board):
        evaluation = 0
        if not self.touch_border(black_board, white_board):
            if self._player_color:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        evaluation += self._EVALUATION_FIRST[position]
                    elif self._exponentiation2[position]&white_board:
                        evaluation -= self._EVALUATION_FIRST[position]
            else:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        evaluation -= self._EVALUATION_FIRST[position]
                    elif self._exponentiation2[position]&white_board:
                        evaluation += self._EVALUATION_FIRST[position]
        else:
            if self._player_color:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        evaluation += self._EVALUATION_MIDDLE[position]
                    elif self._exponentiation2[position]&white_board:
                        evaluation -= self._EVALUATION_MIDDLE[position]
            else:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        evaluation -= self._EVALUATION_MIDDLE[position]
                    elif self._exponentiation2[position]&white_board:
                        evaluation += self._EVALUATION_MIDDLE[position]
        return evaluation

    def check_hash_table(self, hashed_board, hash_key):
        """Save board data which is deeper than 4."""
        if hashed_board in self._hash_log[hash_key].keys():
            return True, self._hash_log[hash_key][hashed_board]
        return False, None

    def save_hash_table(self, hashed_board, hash_key, evaluation, selected, depth):
        if depth < 4:
            return
        self._hash_log[hash_key][hashed_board] = (evaluation, selected)
        return

    def update_file(self):
        with open(self._filename, 'wb') as file_:
            pickle.dump(self._hash_log, file_)
        return

    def min_max(self, black_board, white_board, game_turn, depth, pre_evaluation):
        # If the board is known, return value.
        hashed_board = "".join([str(black_board), str(white_board)])
        hash_key = "".join([str(self._player_color) + str(game_turn) + str(depth)])

        is_exist, saved = self.check_hash_table(hashed_board, hash_key)
        if is_exist:
            evaluation, selected = saved
            return evaluation, selected

        # Calculate evaluation.
        evaluation = self.evaluate_value(black_board, white_board)
        if depth == 0:
            return evaluation, 1

        if game_turn == self._player_color:
            max_evaluation = -1*float('inf')
        else:
            min_evaluation = float('inf')

        reversible = self._othello.board.reversible_area(black_board, white_board, game_turn)

        candidates = []
        for num in range(64):
            if self._exponentiation2[num]&reversible:
                candidates.append(num)

        if self._othello.board.turn_playable(reversible):
            for candidate in candidates:
                new_black_board, new_white_board = self._othello.board.reverse(black_board, white_board, game_turn, self._exponentiation2[candidate])
                count_player, count_opponent = self._othello.board.count_disks(new_black_board, new_white_board, self._player_color)
                count_blank = 64 - count_player - count_opponent
                if self.game_judgement(count_player, count_opponent, count_blank):
                    if self._result == 'WIN':
                        next_evaluation = 10000000000
                    elif self._result == 'LOSE':
                        next_evaluation = -10000000000
                    else:
                        next_evaluation = 0
                else:
                    if game_turn == self._player_color:
                        next_evaluation = self.min_max(new_black_board, new_white_board, game_turn^1, depth-1, max_evaluation)[0]
                    else:
                        next_evaluation = self.min_max(new_black_board, new_white_board, game_turn^1, depth-1, min_evaluation)[0]

                # alpha-bata method(pruning)
                if game_turn == self._player_color:
                    if next_evaluation > pre_evaluation:
                        return pre_evaluation, candidate
                else:
                    if pre_evaluation > next_evaluation:
                        return pre_evaluation, candidate

                if game_turn == self._player_color:
                    if max_evaluation < next_evaluation:
                        max_evaluation = next_evaluation
                        selected = candidate
                else:
                    if next_evaluation < min_evaluation:
                        min_evaluation = next_evaluation
                        selected = candidate
        else:
            if game_turn == self._player_color:
                return self.min_max(black_board, white_board, game_turn^1, depth-1, max_evaluation)
            else:
                return self.min_max(black_board, white_board, game_turn^1, depth-1, min_evaluation)
        if game_turn == self._player_color:
            self.save_hash_table(hashed_board, hash_key, max_evaluation, selected, depth)
            return max_evaluation, selected
        else:
            self.save_hash_table(hashed_board, hash_key, min_evaluation, selected, depth)
            return min_evaluation, selected

    def put_disk(self, othello, depth=3):
        black_board = othello.board._black_board
        white_board = othello.board._white_board
        game_turn = othello.board.game_turn
        self._player_color = game_turn
        self._count_pass = 0
        self._othello = othello
        return self.min_max(black_board, white_board, game_turn, depth, pre_evaluation=float('inf'))[1]