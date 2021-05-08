"""Various strategies for othello.
"""

from collections import deque
import copy
import numpy as np
import pickle
import random

from bitboard import OthelloGame

class Minmax:
    """Find a better move by min-max method.
    """
    __all__ = ["put_disk"]

    def __init__(self, filename='./_trial/strategy/minmax_hash.pkl'):
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

    def game_judgement(self, count_player: int, count_opponent: int, count_blank: int):
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

    # def touch_border(self, black_board: int, white_board: int):
    #     board = (black_board | white_board)
    #     return (board & 0xff818181818181ff)

    def openness(self, black_board: int, white_board: int, game_turn: int, candidate:int):
        """Calculate openness.

        未完成　難しくない？

        Parameters
        ----------
        candidate : int
            Integer from 0 to 63.
        """
        input_ = self._exponentiation2[candidate]
        if game_turn:
            return self.bit_count(black_board), self.bit_count(white_board)
        else:
            return self.bit_count(white_board), self.bit_count(black_board)
        blank_board = ~(black_board | white_board)

        reverse_bit = 0
        for direction in range(8):
            reverse_bit_ = 0
            border_bit = self._othello.board.check_surroundings(input_, direction)
            while (border_bit != 0) and ((border_bit & opponent) != 0):
                reverse_bit_ |= border_bit
                border_bit = self.check_surroundings(border_bit, direction)
            if (border_bit & player) != 0:
                reverse_bit |= reverse_bit_
        

        reversed_disk = []
        for num in range(64):
            if self._exponentiation2[num]&reverse_bit:
                reversed_disk.append(num)
        print("reversed_disk", reversed_disk)


        openness_value = 0
        print(candidate, openness_value)
        return openness_value

    def static_evaluation_function(self, black_board: int, white_board: int, stage: int) -> int:
        """Definition of static function.
        """
        board_evaluation = 0
        if stage < 21:
            if self._player_color:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        board_evaluation += self._EVALUATION_FIRST[position]
                    elif self._exponentiation2[position]&white_board:
                        board_evaluation -= self._EVALUATION_FIRST[position]
            else:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        board_evaluation -= self._EVALUATION_FIRST[position]
                    elif self._exponentiation2[position]&white_board:
                        board_evaluation += self._EVALUATION_FIRST[position]
        else:
            if self._player_color:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        board_evaluation += self._EVALUATION_MIDDLE[position]
                    elif self._exponentiation2[position]&white_board:
                        board_evaluation -= self._EVALUATION_MIDDLE[position]
            else:
                for position in range(64):
                    if self._exponentiation2[position]&black_board:
                        board_evaluation -= self._EVALUATION_MIDDLE[position]
                    elif self._exponentiation2[position]&white_board:
                        board_evaluation += self._EVALUATION_MIDDLE[position]
        return board_evaluation

    def check_hash_table(self, hashed_board: str, hash_key: str):
        """Save board data which is deeper than 4."""
        if hashed_board in self._hash_log[hash_key].keys():
            return True, self._hash_log[hash_key][hashed_board]
        return False, None

    def save_hash_table(self, hashed_board: str, hash_key: str, evaluation: int, selected: tuple, depth: int):
        if depth < 4:
            return
        self._hash_log[hash_key][hashed_board] = (evaluation, selected)
        return

    def update_file(self):
        with open(self._filename, 'wb') as file_:
            pickle.dump(self._hash_log, file_)
        return

    def move_ordering(self, black_board: int, white_board: int, game_turn: int, reversible: int, candidates: list, stage: int) -> list:
        """Define order of moves, so that you can find next move effectively.
        For move ordering, values below are used.
            Opening(0~20) : evaluate_value, available moves
            Middle game(21~47) : evaluate_value
            Endgame(48~64) : number of available moves(Fastest-first find)
        
        Returns
        ----------
        candidates : list of ints
            List of integers orderd by possibility.
        """
        # print("order")

        ordered_candidates = []
        if not reversible:
            return ordered_candidates
        # Killer move(corner)
        if reversible&0x1:
            ordered_candidates.append([1000000, 0])
        if reversible&0x80:
            ordered_candidates.append([1000000, 7])
        if reversible&0x100000000000000:
            ordered_candidates.append([1000000, 56])
        if reversible&0x8000000000000000:
            ordered_candidates.append([1000000, 63])
        # print("init candidates", candidates)
        for number, candidate in enumerate(candidates):
            new_black_board, new_white_board = self._othello.board.reverse(black_board, white_board, game_turn, self._exponentiation2[candidate])

            # openness_value = self.openness(black_board, white_board, game_turn, candidate)
            if stage < 21:
                available_moves = self._othello.board.reversible_area(new_black_board, new_white_board, game_turn^1)
                available_moves = self._othello.board.bit_count(available_moves)
                board_evaluation = self.static_evaluation_function(new_black_board, new_white_board, stage=stage)
                evaluation = -5*available_moves + board_evaluation
                # print(stage, available_moves, board_evaluation)
            elif 21 <= stage < 48:
                board_evaluation = self.static_evaluation_function(new_black_board, new_white_board, stage=stage)
                evaluation = board_evaluation
                # print(stage, board_evaluation)
            else:
                available_moves = self._othello.board.reversible_area(new_black_board, new_white_board, game_turn^1)
                available_moves = self._othello.board.bit_count(available_moves)
                evaluation = -1*available_moves
                # print(stage, available_moves)

            ordered_candidates.append([evaluation, candidate])
        ordered_candidates.sort(reverse=True)
        # ordered_candidates = np.uint64(np.array(ordered_candidates))
        ordered_candidates = np.array(ordered_candidates)
        # print(ordered_candidates)
        return ordered_candidates[:, 1]

    def search_candidates(self, reversible: int) -> list:
        """Count the number of bit awaking.
        
        Parameters
        ----------
        reversible : int
            64-bit intager.

        Returns
        ----------
        candidates : list of ints
            List of integers from 0 to 63.
        """
        candidates = []
        num = 0
        for position in range(64):
            if reversible&self._exponentiation2[position]:
                candidates.append(position)
        return candidates

    def min_max(self, black_board: int, white_board: int, game_turn: int, depth: int, pre_evaluation=-1*float('inf')):
        # If the board is known, return value.
        # print("called, game turn = %d, depth = %d, pre = %f" %(game_turn, depth, pre_evaluation))
        hashed_board = "".join([str(black_board), str(white_board)])
        hash_key = "".join([str(self._player_color) + str(game_turn) + str(depth)])

        is_exist, saved = self.check_hash_table(hashed_board, hash_key)
        if is_exist:
            evaluation, selected = saved
            # print("exist, evaluation = %d, selected = %d, depth = %d" %(evaluation, selected, depth))
            return evaluation, selected

        # Calculate evaluation.
        stage = self._othello.board.bit_count(black_board) + self._othello.board.bit_count(white_board)
        if depth == 0:
            if stage < 21:
            # print("return root evaluation = %d" %(evaluation))
                available_moves = self._othello.board.reversible_area(black_board, white_board, game_turn)
                available_moves = self._othello.board.bit_count(available_moves)
                board_evaluation = self.static_evaluation_function(black_board, white_board, stage)
                evaluation = -5*available_moves + board_evaluation
                return -5*available_moves + board_evaluation, 1
            else:
                return self.static_evaluation_function(black_board, white_board, stage), 1

        if game_turn == self._player_color:
            max_evaluation = -1*float('inf')
        else:
            min_evaluation = float('inf')

        reversible = self._othello.board.reversible_area(black_board, white_board, game_turn)
        if depth > 4:
            pre_candidates = self.search_candidates(reversible)
            candidates = self.move_ordering(black_board, white_board, game_turn, reversible, pre_candidates, stage)
        else:
            candidates = self.search_candidates(reversible)

        # print("pre candidates", candidates)
        if self._othello.board.turn_playable(reversible):
            for candidate in candidates:
                new_black_board, new_white_board = self._othello.board.reverse(black_board, white_board, game_turn, self._exponentiation2[candidate])
                count_player, count_opponent = self._othello.board.count_disks(new_black_board, new_white_board, self._player_color)
                count_blank = 64 - count_player - count_opponent
                if self.game_judgement(count_player, count_opponent, count_blank):
                    if self._result == 'WIN':
                        next_evaluation = count_player*1000
                    elif self._result == 'LOSE':
                        next_evaluation = -count_opponent*1000
                    else:
                        next_evaluation = 0
                else:
                    if game_turn == self._player_color:
                        # print('call function, candidate = %d, depth = %d' %(candidate, depth))
                        next_evaluation = self.min_max(new_black_board, new_white_board, game_turn^1, depth-1, max_evaluation)[0]
                    else:
                        # print('call function, candidate = %d, depth = %d' %(candidate, depth))
                        next_evaluation = self.min_max(new_black_board, new_white_board, game_turn^1, depth-1, min_evaluation)[0]

                # alpha-bata method(pruning)
                if game_turn == self._player_color:
                    # print('beta cut, pre=%f < next=%f or not' %(pre_evaluation, next_evaluation))
                    if next_evaluation > pre_evaluation:
                        # print('cut, candidate = %d, depth = %d' %(candidate, depth))
                        return pre_evaluation, candidate
                else:
                    # print('alpha cut, pre=%f > next=%f or not' %(pre_evaluation, next_evaluation))
                    if pre_evaluation > next_evaluation:
                        # print('cut, candidate = %d, depth = %d' %(candidate, depth))
                        return pre_evaluation, candidate

                if game_turn == self._player_color:
                    if max_evaluation < next_evaluation:
                        max_evaluation = next_evaluation
                        selected = candidate
                        # print("new max", max_evaluation)
                else:
                    if next_evaluation < min_evaluation:
                        min_evaluation = next_evaluation
                        selected = candidate
                        # print("new min", min_evaluation)
        else:
            # print('pass', game_turn, depth)
            if game_turn == self._player_color:
                return self.min_max(black_board, white_board, game_turn^1, depth-1, max_evaluation)
            else:
                return self.min_max(black_board, white_board, game_turn^1, depth-1, min_evaluation)
        if game_turn == self._player_color:
            if depth > 4:
                self.save_hash_table(hashed_board, hash_key, max_evaluation, selected, depth)
            # print("final value = %f, selected = %d, game turn %d, depth = %d" %(max_evaluation, selected, game_turn, depth))
            return max_evaluation, selected
        else:
            if depth > 4:
                self.save_hash_table(hashed_board, hash_key, min_evaluation, selected, depth)
            # print("final value = %f, selected = %d, game turn %d, depth = %d" %(min_evaluation, selected, game_turn, depth))
            return min_evaluation, selected

    def put_disk(self, othello, depth=6):
        # print()
        # print()
        # print("initial call")
        black_board = othello.board._black_board
        white_board = othello.board._white_board
        game_turn = othello.board.game_turn
        self._player_color = game_turn
        self._count_pass = 0
        self._othello = othello
        # x = self.min_max(black_board, white_board, game_turn, depth, pre_evaluation=float('inf'))[1]
        # print(x)
        # return int(x)
        return int(self.min_max(black_board, white_board, game_turn, depth, pre_evaluation=float('inf'))[1])