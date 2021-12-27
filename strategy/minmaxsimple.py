"""Various strategies for othello.
"""

import pickle


class MinmaxSimple:
    """Find a better move by min-max method."""
    __all__ = ["put_disk"]

    def __init__(self, filename='./strategy/minmaxsimple_hash.pkl'):
        self._filename = filename
        try:
            with open(filename, 'rb') as file_:
                self._hash_log = pickle.load(file_)
        except FileNotFoundError:
            self._hash_log = {}
        for color in ["1", "0"]:
            for turn in ['1', '0']:
                for depth in map(str, range(10)):
                    key = "".join([color, turn, depth])
                    if key not in self._hash_log.keys():
                        self._hash_log[key] = {}

        self._EVALUATION_TABLE = [
            # 1st evaluation table
            [
                30,  -12,   0,  -1,  -1,   0, -12,  30,
                -12, -15,  -3,  -3,  -3,  -3, -15, -12,
                0,    -3,   0,  -1,  -1,   0,  -3,   0,
                -1,   -3,  -1,  -1,  -1,  -1,  -3,  -1,
                -1,   -3,  -1,  -1,  -1,  -1,  -3,  -1,
                0,    -3,   0,  -1,  -1,   0,  -3,   0,
                -12, -15,  -3,  -3,  -3,  -3, -15, -12,
                30,  -12,   0,  -1,  -1,   0, -12,  30,
            ],
            # 2nd evaluation table
            [
                120, -20,  20,   5,   5,  20, -20, 120,
                -20, -40,  -5,  -5,  -5,  -5, -40, -20,
                20,   -5,  15,   3,   3,  15,  -5,  20,
                5,    -5,   3,   3,   3,   3,  -5,   5,
                5,    -5,   3,   3,   3,   3,  -5,   5,
                20,   -5,  15,   3,   3,  15,  -5,  20,
                -20, -40,  -5,  -5,  -5,  -5, -40, -20,
                120, -20,  20,   5,   5,  20, -20, 120,
            ],
        ]

        self._EXP2 = [pow(2, num) for num in range(64)]
        return

    def touch_border(self, white_board, black_board):
        board = (white_board | black_board)
        if board & 0xff818181818181ff:
            return 1
        return 0

    def evaluate_value(self, white_board, black_board):
        evaluation = 0
        board = [white_board, black_board]

        # If disk does not touch the border,
        # phase is False and TABLE[0] is called.
        phase = self.touch_border(white_board, black_board)
        for position in range(64):
            if (self._EXP2[position] & board[self._player_color ^ 1]):
                evaluation += self._EVALUATION_TABLE[phase][position]
            if (self._EXP2[position] & board[self._player_color]):
                evaluation -= self._EVALUATION_TABLE[phase][position]
        return evaluation

    def check_hash_table(self, hashed_board, hash_key):
        """Save board data which is deeper than 4."""
        if hashed_board in self._hash_log[hash_key].keys():
            return True, self._hash_log[hash_key][hashed_board]
        return False, None

    def save_hash_table(
            self, hashed_board, hash_key, evaluation, selected, depth
            ):
        if depth < 4:
            return
        self._hash_log[hash_key][hashed_board] = (evaluation, selected)
        return

    def update_file(self):
        with open(self._filename, 'wb') as file_:
            pickle.dump(self._hash_log, file_)
        return

    def min_max(
            self, white_board, black_board, game_turn, depth, pre_evaluation
            ):
        # If the board is known, return value.
        hashed_board = "".join([str(white_board), str(black_board)])
        hash_key = "".join([str(self._player_color)+str(game_turn)+str(depth)])

        is_exist, saved = self.check_hash_table(hashed_board, hash_key)
        if is_exist:
            evaluation, selected = saved
            return evaluation, selected

        # Calculate evaluation.
        evaluation = self.evaluate_value(white_board, black_board)
        if depth == 0:
            return evaluation, 1

        if game_turn == self._player_color:
            max_evaluation = -1 * float('inf')
        else:
            min_evaluation = float('inf')

        reversible = self._othello.board.reversible_area(
            game_turn, white_board, black_board
            )

        candidates = []
        for num in range(64):
            if self._EXP2[num] & reversible:
                candidates.append(num)

        if self._othello.board.turn_playable(
            game_turn, white_board, black_board
        ):
            for candidate in candidates:
                new_white_board, new_black_board = \
                    self._othello.board.put_disk(
                        game_turn, self._EXP2[candidate], False,
                        white_board, black_board,
                    )
                count_white, count_black = self._othello.board.count_disks(
                    new_white_board, new_black_board
                )
                if self._player_color:
                    count_player, count_opponent = count_black, count_white
                else:
                    count_player, count_opponent = count_white, count_black
                count_blank = 64 - count_player - count_opponent
                if self._othello.judge_game(
                        count_player, count_opponent, count_blank):
                    if self._result == 'WIN':
                        next_evaluation = 10000000000
                    elif self._result == 'LOSE':
                        next_evaluation = -10000000000
                    else:
                        next_evaluation = 0
                else:
                    if game_turn == self._player_color:
                        next_evaluation = self.min_max(
                            new_white_board, new_black_board,
                            game_turn ^ 1, depth-1, max_evaluation,
                            )[0]
                    else:
                        next_evaluation = self.min_max(
                            new_white_board, new_black_board,
                            game_turn ^ 1, depth-1, min_evaluation,
                            )[0]

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
                return self.min_max(
                    white_board, black_board,
                    game_turn ^ 1, depth-1, max_evaluation,
                    )
            else:
                return self.min_max(
                    white_board, black_board,
                    game_turn ^ 1, depth-1, min_evaluation,
                    )
        if game_turn == self._player_color:
            self.save_hash_table(
                hashed_board, hash_key, max_evaluation, selected, depth)
            return max_evaluation, selected
        else:
            self.save_hash_table(
                hashed_board, hash_key, min_evaluation, selected, depth)
            return min_evaluation, selected

    def put_disk(self, othello, depth=3):
        white_board, black_board = othello.board.return_board()
        game_turn = othello.game_turn
        self._player_color = game_turn
        self._count_pass = 0
        self._othello = othello
        return self.min_max(
            white_board, black_board, game_turn,
            depth, pre_evaluation=float('inf'),
            )[1]
